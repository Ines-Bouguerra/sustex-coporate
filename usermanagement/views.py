from django.shortcuts import render
# user_management/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from usermanagement.functions import CustomValidator
from usermanagement.models import User
from .serializers import CustomUserSerializer, UpdateUserSerializer
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
import json
from django.core import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from django.core.exceptions import ValidationError
from drf_yasg import openapi
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.contrib.auth.backends import ModelBackend
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF Users",
                     operation_description="API TO GET LIST OF Users",)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getAllUsers(request):
    """Get all users from database"""
    list_users = []
    if (request.method == 'GET'):
        users = User.objects.all()
        user_dict = serializers.serialize("json", users)
        res = json.loads(user_dict)
        for i in range(0, len(res)):
            res[i].pop('model')
            id = res[i]['pk']
            res[i].pop('pk')
            res[i]['fields'].pop('password')
            res[i]['fields']['id'] = id
            list_users.append(res[i]['fields'])
        return JsonResponse({"list_users":list_users})

@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET USER BY ID",
                     operation_description="API TO GET USER BY ID",)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def getUser(request, id):
    """Get user by ID from database"""
    if request.method == 'GET':
        try:
            user = User.objects.get(pk=id)
            user_dict = serializers.serialize("json", [user])  # Serializing single object
            res = json.loads(user_dict)
            user_json = res[0]['fields']
            user_json['id'] = res[0]['pk']
            del user_json['password']  # Remove password field
            return JsonResponse({"user": user_json})
        except User.DoesNotExist:
            return JsonResponse({"msg": "User not found!"}, status=404)

@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                    request_body=CustomUserSerializer,
                     operation_summary="API TO Create New USER",
                     operation_description="API TO Create New USER",)

@api_view(['POST'])
@permission_classes([AllowAny]) 
def createUser(request):
    """Create user"""
    if request.method == 'POST':
        data = request.data
        try:
            CustomValidator.validate_password(data['password'])
        except ValidationError as e:
            return JsonResponse({"msg": str(e)},status=400)
        data['password']=make_password(data.get('password'))
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"msg":"User added successfully!"}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"msg":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
      
@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE USER",
                     operation_description="API TO DELETE USER",)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_user(request, id):
    """Delete user """
    if (request.method == 'DELETE'):
        if User.objects.filter(pk=id).exists():
            user = User.objects.get(pk=id)
            user.delete()
            return JsonResponse({"msg":"User deleted successfully!"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"msg":"User not found !"}, status=status.HTTP_404_NOT_FOUND)
            
        
        
@swagger_auto_schema('PUT', responses={200: 'Created', 400: 'Bad Request'}, 
                    request_body=UpdateUserSerializer,
                     operation_summary="API TO UPDATE  USER",
                     operation_description="API TO UPDATE  USER",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
def modifyUser(request, id):
    if request.method == 'PUT':
        try:
            user_object = User.objects.get(pk=id)
        except User.DoesNotExist:
            return JsonResponse({"msg": "User not found!"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        serializer = UpdateUserSerializer(user_object, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"msg": "User updated successfully!"}, status=status.HTTP_200_OK)
        return JsonResponse({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='PUT',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['old_password', 'new_password'],
        properties={
            'old_password': openapi.Schema(type=openapi.TYPE_STRING),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE Change Password User",
    operation_description="This API helps us to update User's password."
)

@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def changePassword(request, id):
    msg = ""
    if (request.method == 'PUT'):
            user_object = User.objects.get(pk=id)
            data = request.data
            old_password = data['old_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']
            try:
                CustomValidator.validate_password(new_password)
            except ValidationError as e:
                return JsonResponse({"msg": str(e)},status=400)
            if new_password != confirm_password:
                msg = "Passwords do not match. Please try again."
                status=400
            else:
                check_password_var=check_password(old_password,user_object.password)
                if check_password_var:
                    user_object.password = make_password(new_password)
                    user_object.save()
                    msg = "Password change successfully!"
                    status=200  
                else:
                    msg = "Your old password is incorrect!"
                    status=400  
            return JsonResponse({"msg": msg},status=status)
class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None      
@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING,format='email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="This API helps us to authenticate ",
    operation_description="This API helps us to authenticate "
)


# @api_view(['POST'])
# @permission_classes([AllowAny])
# # @ensure_csrf_cookie
# def authentication(request):
#     if request.method == 'POST':
#         data = request.data
#         email = data.get('email')
#         password = data.get('password')
#         user = authenticate(request, email=email, password=password)
#         if user is not None:
#             login(request, user)
#             print(request.COOKIES)
#             response = JsonResponse({"msg": "User logged successfully!",
#                                      "csrftoken":request.COOKIES.get('csrftoken')}, status=200)
#             return response
#         else:
#             return JsonResponse({"msg": "Invalid email or password!"}, status=200)            
 
@api_view(['POST'])
@permission_classes([AllowAny])
# @csrf_protect
def authentication(request):
    if request.method == 'POST':
        data = request.data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            response = JsonResponse({"msg": "User logged in successfully!"}, status=200)
            # Set CSRF cookie in the response
            response.set_cookie('csrftoken', request.META.get('CSRF_COOKIE'))
            return response
        else:
            return JsonResponse({"msg": "Invalid email or password!"}, status=400) 
@api_view(['POST'])
@authentication_classes([SessionAuthentication])  
def logout_view(request):
    logout(request)
    # clear the user's session data
    Session.objects.filter(session_key=request.session.session_key).delete()  
    return JsonResponse({"msg": "User logged out successfully!"},status=200)
            