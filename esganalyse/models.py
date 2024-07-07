from django.db import models
from django.utils import timezone
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
# Create your models here.
class Campany(models.Model):
    id = models.AutoField(primary_key=True) 
    campany_name=models.CharField(max_length=200,null=True)
    year=models.CharField(max_length=200,null=True)
    total_env_label = models.IntegerField(null=True)
    total_soc_label = models.IntegerField(null=True)
    total_gov_label = models.IntegerField(null=True)
    total_env_neutral = models.IntegerField(null=True)
    total_env_opportunity = models.IntegerField(null=True)
    total_env_risk = models.IntegerField(null=True)
    total_soc_neutral = models.IntegerField(null=True)
    total_soc_opportunity = models.IntegerField(null=True)
    total_soc_risk = models.IntegerField(null=True)
    total_gov_neutral = models.IntegerField(null=True)
    total_gov_opportunity = models.IntegerField(null=True)
    total_gov_risk = models.IntegerField(null=True)
    total_e_score = models.FloatField(null=True)
    total_s_score = models.FloatField(null=True)
    total_g_score = models.FloatField(null=True)
    total_esg_score = models.FloatField(null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False,null=True)
    updated_at = models.DateTimeField(default=timezone.now,editable=False,null=True)

    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(Campany, self).save(*args, **kwargs)
    def __str__(self):
            return self.campany_name
    class Meta:
        db_table = 'campany'
        
class CampanyDetails(models.Model):
    id = models.AutoField(primary_key=True) 
    campany = models.ForeignKey(Campany, on_delete=models.CASCADE)
    factors=models.TextField(max_length=500,null=False)
    category=models.CharField(max_length=200,null=True)
    score_class=models.FloatField(null=True)
    sentiment = models.CharField(max_length=200,null=True)
    score_sentiment = models.FloatField(null=True)
    e_score = models.FloatField(null=True)
    s_score = models.FloatField(null=True)
    g_score = models.FloatField(null=True)
    recommandation= models.CharField(max_length=200,null=True)
    # esg_score = models.FloatField(null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False,null=True)
    updated_at = models.DateTimeField(default=timezone.now,editable=False,null=True)
    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super(CampanyDetails, self).save(*args, **kwargs)
    def __str__(self):
            return self.campany_name
    class Meta:
        db_table = 'campany_details'
        

              
         