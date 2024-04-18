from django.shortcuts import render
# user_management/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from usermanagement.functions import CustomValidator
from usermanagement.models import User
from .serializers import CustomUserSerializer, PasswordSerializer, UpdateUserSerializer
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
    """Get user  by ID from database"""
    if (request.method == 'GET'):
        user = User.objects.filter(id=id)
        user_dict = serializers.serialize("json", user)
        res = json.loads(user_dict)
        res[0].pop('model')
        id = res[0]['pk']
        res[0].pop('pk')
        res[0]['fields'].pop('password')
        res[0]['fields']['id'] = id
        user_json = res[0]['fields']
        return JsonResponse({"user": user_json})

@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                    request_body=CustomUserSerializer,
                     operation_summary="API TO Create New USER",
                     operation_description="API TO Create New USER",)

@api_view(['POST'])
@authentication_classes([AllowAny])
@permission_classes([IsAuthenticated])
def createUser(request):
    """Create user"""
    if request.method == 'POST':
        data = request.data
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"msg":"User added successfully!"}, status=status.HTTP_201_CREATED)
        return JsonResponse({"msg":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
      
@swagger_auto_schema('DELETE', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO DELETE USER",
                     operation_description="API TO DELETE USER",)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
def delete_user(request, id):
    """Delete user """
    if (request.method == 'DELETE'):
        user = User.objects.get(id=id)
        user.delete()
        return JsonResponse({"msg":"User deleted successfully!"}, status=status.HTTP_200_OK)
    
        
@swagger_auto_schema('POST', responses={200: 'Created', 400: 'Bad Request'}, 
                    request_body=UpdateUserSerializer,
                     operation_summary="API TO UPDATE  USER",
                     operation_description="API TO UPDATE  USER",)
@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def modifyUser(request, id):
    if (request.method == 'PUT'):
        user_object = User.objects.filter(id=id)
        data = request.data
        serializer = UpdateUserSerializer(user_object,data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"msg":"User updated successfully!"}, status=status.HTTP_200_OK)
        return JsonResponse({"msg":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='PUT',
    request_body=PasswordSerializer,
    responses={200: 'Created', 400: 'Bad Request'},
    operation_summary="API TO UPDATE Change Password User ",
    operation_description="This API help us to update User's password added ",
)

@api_view(['PUT'])
@authentication_classes([SessionAuthentication])
#@permission_classes([IsAuthenticated])
def changePassword(request, id):
    msg = ""
    if (request.method == 'PUT'):
            user_object = User.objects.get(id=id)
            data = request.data
            old_password = data['old_password']
            new_password = data['new_password']
            confirm_password = data['confirm_password']
            try:
                CustomValidator.validate_password(new_password)
            except ValidationError as e:
                return JsonResponse({"msg": str(e)},status=status.HTTP_400_BAD_REQUEST)
            if new_password != confirm_password:
                msg = "Passwords do not match. Please try again."
            else:
                check_password=check_password(old_password,user_object.password)
                if check_password:
                    user_object.password = make_password(new_password)
                    user_object.save()
                    msg = "Password change successfully!"
                    status=200  
                else:
                    msg = "Your old password is incorrect!"
                    status=400  
            return JsonResponse({"msg": msg},status=status)

@api_view(['POST'])
@authentication_classes([AllowAny])
def authentication(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('success_page')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'login.html', {'error': 'Invalid email or password'})
    else:
        return render(request, 'login.html')
