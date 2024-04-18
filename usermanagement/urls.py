# myproject/urls.py
from django.urls import path
import views
urlpatterns = [
    path('login/', views.authentication, name='login'),
    path('getAllUsers', views.getAllUsers, name="getAllUsers"),
    path('getUser/<int:id>', views.getUser, name="getUser"),
    path('createUser', views.createUser, name="createUser"),
    path('deleteUser/<int:id>', views.delete_user, name="deleteUser"),
    path('modifyUser/<int:id>', views.modifyUser, name="modifyUser"),
    path('userChangePW/<int:id>', views.changePassword, name="userChangePW"),
]
