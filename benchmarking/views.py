from benchmarking.functions import get_info_campany
from esganalyse.models import Campany
from django.http import JsonResponse
import json
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import logout
from django.core import serializers

@swagger_auto_schema(
    method='POST',
    responses={
        200: 'Created',
        400: 'Bad Request'
    },
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['campany1', 'campany2', 'date'],
        properties={
            'campany1': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING)
            ),
            'campany2': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING)
            ),
            'date': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    operation_summary="API TO GET BENCHMARK INFO OF SELECTED COMPANY AND TIME",
    operation_description="API TO GET BENCHMARK INFO OF SELECTED COMPANY AND TIME"
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_benchmark_info(request):
    """Get benchmark info from database"""
    if (request.method == 'POST'):
        data = request.data
        campany1=data.get('campany1',[])
        campany2=data.get('campany2',[])
        date=data.get('date',None)
        list_infos1=[]
        list_infos2=[]
        if len(campany1)!=0 and len(campany2)!=0  and date is not None :
            for x in campany1:
                list_infos1.append({x:get_info_campany(x,date)})
            for y in campany2:
                list_infos2.append({y:get_info_campany(y,date)})
            return JsonResponse({"list_infos1":list_infos1,"list_infos2":list_infos2},status=200)
        else:
            return JsonResponse({"msg":"Veuillez remplir toutes les informations!"},status=400)
        
        
        
@swagger_auto_schema('GET', responses={200: 'Created', 400: 'Bad Request'}, 
                     operation_summary="API TO GET LIST OF CAMPANIES",
                     operation_description="API TO GET LIST OF CAMPANIES",)
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_campanies(request):
    """Get campanies from database"""
    if (request.method == 'GET'):
        campany_object= Campany.objects.all()
        campany_dict = serializers.serialize("json", campany_object)
        res = json.loads(campany_dict)
        list_campanies=[]
        for i in range(0, len(res)):
            print(res[i])
            list_campanies.append(res[i]['fields']['campany_name'])
        return JsonResponse({"campanies":list_campanies},status=200)