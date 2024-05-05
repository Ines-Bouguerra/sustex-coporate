from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
# Create your views here.
from django.shortcuts import render
from .forms import UploadFileForm
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import  AllowAny
@swagger_auto_schema(
    method='post',
    operation_summary="Upload File",
    operation_description="Endpoint to upload a file.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['file'],
        properties={
          'file': openapi.Schema(type=openapi.TYPE_FILE),
        },
    ),
    responses={200: openapi.Response('Success', schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
)
@api_view(['POST'])
@permission_classes([AllowAny]) 
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            saved_file = form.save()
            file_path = saved_file.file.url 
            return Response({"message": "File uploaded successfully.","path":file_path }, status=201)  # Return a success response
        else:
            return Response(form.errors, status=400)  # Return validation errors if form is invalid
    # else:
    #     form = UploadFileForm()
    #     return Response({"message": "File uploaded successfully."}, status=201) 