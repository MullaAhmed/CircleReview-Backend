from django.db import models
from Employee.models import *


class FeedbackForm(models.Model):
    company_name=models.CharField(max_length=50)
    time=models.DateTimeField(auto_now_add=True)
    team=models.CharField(max_length=100) # Can be replaced by Department name as a foregin key
    status=models.CharField(max_length=100) #Active or Paused
    people=models.ManyToManyField(UserProfile,related_name='people')
  

    self_review=models.JSONField(blank=True)
    peer_review=models.JSONField(blank=True)
    manager_review=models.JSONField(blank=True)
    hr_review=models.JSONField(blank=True)
    external_review=models.JSONField(blank=True)

    def __str__(self):
        return f'{self.time}-{self.team}'


class Feedback(models.Model):
    employee_name=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    company_name=models.CharField(max_length=50)
    status=models.JSONField()
    nominations=models.JSONField()
    feedback_form=models.IntegerField() #id of form

    self_review=models.JSONField()
    peer_review=models.JSONField()
    manager_review=models.JSONField()
    hr_review=models.JSONField()
    external_review=models.JSONField()
    
    

    def __str__(self):
        return str(self.employee_name.user)