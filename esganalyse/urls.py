from django.urls import path
from esganalyse import views
urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
   
]
