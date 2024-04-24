from rest_framework import serializers
from .models import Campany, CampanyDetails
class CampanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Campany
        fields =[
                "campany_name",
                "year",
                "total_env_label",
                "total_soc_label",
                "total_gov_label",
                "total_env_neutral",
                "total_env_opportunity",
                "total_env_risk",
                "total_soc_neutral",
                "total_soc_opportunity",
                "total_soc_risk",
                "total_gov_neutral",
                "total_gov_opportunity",
                "total_gov_risk",
                "total_e_score",
                "total_s_score",
                "total_g_score",
                "total_esg_score"
        ]
        
class CampanyDetailsSerializer(serializers.ModelSerializer):
    campany = serializers.PrimaryKeyRelatedField(queryset=Campany.objects.all())
    class Meta:
            model = CampanyDetails
            fields = ['factors','category','score_class',
                      'sentiment','score_sentiment',
                      'e_score','s_score','g_score',
                      ]