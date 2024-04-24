from rest_framework import serializers
from .models import  User

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email', 'password']

    # def create(self, validated_data):
    #     validated_data['password'] = make_password(validated_data.get('password'))
    #     return User.objects.create(**validated_data)
    
    
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email', ]
        
# class PasswordSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['old_password','new_password', 'confirm_password']