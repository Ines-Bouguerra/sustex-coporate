from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from benchmarking.funcrions import get_info_campany
from esganalyse.models import Campany
from usermanagement.functions import CustomValidator
from usermanagement.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
import json
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
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                      request_body=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['campany1', 'campany2','date1','date2'],
                    properties={
                        'campany1': openapi.Schema(type=openapi.TYPE_STRING),
                        'campany2': openapi.Schema(type=openapi.TYPE_STRING),
                        'date1': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'date2': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                ),
                     operation_summary="API TO GET BENCKMARK INFO OF SELETCTED CAMPANY AND TIME",
                     operation_description="API TO GET BENCKMARK INFO OF SELETCTED CAMPANY AND TIME",)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_benchmark_info(request):
    """Get benchmark info from database"""
    if (request.method == 'GET'):
        data = request.data
        campany1=data.get('campany1',None)
        campany2=data.get('campany1',None)
        date1=data.get('campany1',None)
        date2=data.get('campany1',None)
        list_infos1=get_info_campany(campany1,date1)
        list_infos2=get_info_campany(campany2,date2)
        return JsonResponse({f"{campany1}_{date1}":list_infos1,f"{campany2}_{date2}":list_infos2})