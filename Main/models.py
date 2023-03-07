from django.db import models

# Create your models here.

class UserProfile(models.Model):

    name=models.CharField(max_length=50)
    phone_number=models.IntegerField(null=True)
    email=models.EmailField(max_length=50,unique=True,null=False)
    gender=models.CharField(max_length=50)


    employee_id= models.CharField(max_length=50)
    position=models.CharField(max_length=50) 
    manager=models.CharField(max_length=50)
    team_name=models.CharField(max_length=50)
    company_name=models.CharField(max_length=50,null=True)
    
    doj=models.DateField(null=True)
    dob=models.DateField(null=True)

    cohesive_role=models.CharField(max_length=50)
    cohesive_user_id= models.IntegerField()
    cohesive_user_name=models.CharField(max_length=50)
    cohesive_workspace_id=models.IntegerField()
    cohesive_workspace_name=models.CharField(max_length=50)

    def __str__(self):
        return self.employee_id

class UserRelation(models.Model):
    # u1= employee
    # u2= manager/peer/other
    # U2 is manager of u1
    user_1=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    user_2=models.CharField(max_length=50)
    relation=models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user_1.id} --> {self.user_2}"

class FeedbackForm(models.Model):
    survey_name=models.CharField(max_length=100,default="Feedback Form")
    company_name=models.CharField(max_length=50)
    time=models.DateTimeField(auto_now_add=True)
    
    status=models.CharField(max_length=100) #Active or Paused
    people=models.ManyToManyField(UserProfile,related_name='people')
    completion_rate=models.IntegerField()
  

    self_review=models.JSONField(blank=True)
    peer_review=models.JSONField(blank=True)
    manager_review=models.JSONField(blank=True)
    direct_report_review=models.JSONField(blank=True)
    # cross_functional_review=models.JSONField(blank=True)

    def __str__(self):
        return f'{self.id}-({self.time})-{self.survey_name}'


class Feedback(models.Model):
    user_from=models.CharField(max_length=50)
    user_for=models.CharField(max_length=50)
    feedback_type=models.CharField(max_length=50) #self,peer,manager,direct_report,cross_functional
    company_name=models.CharField(max_length=50)
    form_id=models.IntegerField()
    status=models.CharField(max_length=50,default="Pending") #Pending,Completed
    questions_answers=models.JSONField()

    def __str__(self):
        return f"({self.form_id}) {self.user_from} --> {self.user_for}"

class FeedbackStatus(models.Model):
    user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    form_id=models.ForeignKey(FeedbackForm,on_delete=models.DO_NOTHING)
    status=models.CharField(max_length=50) #Pending,Completed

    def __str__(self):
        return f"({self.form_id}) {self.user.employee_id} --> {self.form_id.survey_name}"