from django.urls import path
from benchmarking import views
urlpatterns = [
    path('benchmark_campany/', views.get_benchmark_info, name='benchmark_campany'),
    path('companies/', views.get_companies, name='companies'),
    path('check_compliance/', views.check_document_compliance, name='check_compliance'),
    path('check_due_diligence/', views.check_due_diligence, name='check_due_diligence'),

  
]
