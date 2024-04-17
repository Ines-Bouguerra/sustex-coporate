# myproject/urls.py
from django.urls import path
from .views import CustomUserCreate,login_view
urlpatterns = [
    path('addUser/', CustomUserCreate.as_view(), name='user-create'),
    path('login/', login_view, name='login'),
]
