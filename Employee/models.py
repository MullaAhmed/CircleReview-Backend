from django.db import models

# Create your models here.

class UserProfile(models.Model):
    company_name=models.CharField(max_length=50)
    user= models.CharField(max_length=50)  # models.OneToOneField(User,on_delete=models.CASCADE)
    email=models.EmailField(max_length=50,unique=True,null=False)
    name= models.CharField(max_length=50)
    team_name=models.CharField(max_length=50)
    dept_name=models.CharField(max_length=50)
    position=models.CharField(max_length=50) 
    related_people=models.JSONField()
    review_status=models.JSONField()
    nominations=models.JSONField()

    def __str__(self):
        return self.user

class Team(models.Model):
    company_name=models.CharField(max_length=50)
    team_name=models.CharField(max_length=50)
    team_lead=models.CharField(max_length=50)
    team_members=models.ManyToManyField(UserProfile)
    team_description=models.CharField(max_length=50)

    def __str__(self):
        return self.team_name


