from django.db import models

# Create your models here.
class UserProfile(models.Model):
    
    email=models.EmailField(max_length=50,unique=True,null=False)
    name= models.CharField(max_length=50)
    position=models.CharField(max_length=50) 
   
   
    cohesieve_role=models.CharField(max_length=50)
    cohesieve_user_id= models.IntegerField()
    cohesieve_user_name=models.CharField(max_length=50)
    cohesieve_workspace_id=models.IntegerField()
    cohesieve_workspace_name=models.CharField(max_length=50)


    related_people=models.JSONField()
    review_status=models.JSONField()
    nominations=models.JSONField()

    def __str__(self):
        return self.name