from django.urls import path
from benchmarking import views
urlpatterns = [
    path('benchmark_campany/', views.get_benchmark_info, name='benchmark_campany'),
    path('campanies/', views.get_campanies, name='campanies'),
  
]
