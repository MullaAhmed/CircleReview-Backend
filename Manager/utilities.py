from django.conf import settings
from Employee.models import *
from django.core.mail import send_mail
from .models import *
from.serializers import *
from django.db.models import Q # Multi crteria queries


def send_email_team(people):
    for i in people:
        subject = 'Review Survey'
        person=UserProfile.objects.get(id=int(i))
        
        message = f'Hi {person.name}, the review survey is out. Please visit <link> and fill yours'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [person.email, ]
        send_mail( subject, message, email_from, recipient_list )


def send_remainder_emails(people,manager): 
    recipient_list = [manager]
    for i in people:
        print(i)
        subject = 'Review Survey'
        person=UserProfile.objects.get(id=int(i))
        recipient_list.append(person.email)
        
    message = f'Hi, the review survey is out. Please visit <link> and fill your self review and review for your peers.'
    email_from = settings.EMAIL_HOST_USER
    
    send_mail( subject, message, email_from, recipient_list ) 

def create_feedback(data,id):
    
    for i in data['people']:
        data={
            "employee_name":i,
            "company_name":data['company_name'],
            "feedback_form":id,
            
            "status":{
                "self_review":"Pending",
                "peer_review":"Pending",
                "manager_review":"Pending",
                "hr_review":"Pending",
                "external_review":"Pending",
            },
              
            "nominations":{
                "peer_review":"Pending",
                "manager_review":"Pending",
                "hr_review":"Pending",
                "external_review":"Pending"
        },

            "self_review":data['self_review'],
            "peer_review":data['peer_review'],
            "manager_review":data['manager_review'],
            "hr_review":data['hr_review'],
            "external_review":data['external_review']
        }
    
        serializer = FeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print("done")
        else:
            print(serializer.errors)
        
def get_nominations(id):

    employee=UserProfile.objects.get(id=id)
    team=Team.objects.get(Q(team_name=employee.team_name) & Q(company_name=employee.company_name))
    manager=UserProfile.objects.get(Q(name=team.team_lead) & Q(company_name=employee.company_name))
    
    return 

""""nominations":{
                "peer_review":"Pending",
                "manager_review":"Pending",
                "hr_review":"Pending",
                "external_review":"Pending"
        }"""