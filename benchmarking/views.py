from benchmarking.functions import get_info_campany
from esganalyse.models import Campany
from django.http import JsonResponse
import json
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import logout
from django.core import serializers
from benchmarking.check_compliance import check_compliance, parse_criteria_from_text, extract_text_from_pdf
from benchmarking.scoring_compliance import check_due_diligence_def, criteria
import pandas as pd


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
# @authentication_classes([SessionAuthentication])
# @permission_classes([IsAuthenticated])
@permission_classes([AllowAny])
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
        
        

@api_view(['GET'])
@permission_classes([AllowAny])
def get_companies(request):
    companies = Campany.objects.all()
    unique_companies = list(set(campany.campany_name for campany in companies))
    return JsonResponse({"companies": unique_companies}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_document_compliance(request):
    """Check document compliance with GDPR and CCPA"""
    if request.method == 'POST':
        file = request.FILES.get('file', None)
        print("file",file)
        if file:
            if file.name.endswith('.csv'):
                data = pd.read_csv(file)
                document_text = data.to_string()
            elif file.name.endswith('.xlsx'):
                data = pd.read_excel(file)
                document_text = data.to_string()
            elif file.name.endswith('.pdf'):
                document_text = extract_text_from_pdf(file)
            else:
                return JsonResponse({"msg": "Format de fichier non supporté!"}, status=400)
            # get file from benchmarking folder
            criteria_pdf_path = 'benchmarking/SEC.pdf' 
            pdf_text = extract_text_from_pdf(criteria_pdf_path)
            criteria = parse_criteria_from_text(pdf_text)

            compliance_results = check_compliance(document_text, criteria)
            return JsonResponse(compliance_results, status=200)
        else:
            return JsonResponse({"msg": "Veuillez fournir un fichier!"}, status=400)
    """Check document compliance with GDPR and CCPA"""
    if request.method == 'POST':
        data = request.data
        document_text = data.get('document_text', None)
        
        if document_text:
            compliance_results = check_compliance(document_text, criteria)
            return JsonResponse(compliance_results, status=200)
        else:
            return JsonResponse({"msg": "Veuillez fournir le texte du document!"}, status=400)
        

@api_view(['POST'])
@permission_classes([AllowAny])
def check_due_diligence(request):
    if request.method == 'POST':
        file = request.FILES.get('file', None)
        if file:
            if file.name.endswith('.csv'):
                data = pd.read_csv(file)
                document_text = data.to_string()
            elif file.name.endswith('.xlsx'):
                data = pd.read_excel(file)
                document_text = data.to_string()
            elif file.name.endswith('.pdf'):
                document_text = extract_text_from_pdf(file)
            else:
                return JsonResponse({"msg": "Format de fichier non supporté!"}, status=400)
            
            compliance_results = check_due_diligence_def(document_text, criteria)
            return JsonResponse(compliance_results, status=200)
        
        else:
            return JsonResponse({"msg": "Veuillez fournir un fichier!"}, status=400)
        
