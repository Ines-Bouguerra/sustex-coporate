from django.urls import path
from benchmarking import views
urlpatterns = [
    path('benchmarking/', views.get_benchmark_info, name='benchmarking'),
  
]
