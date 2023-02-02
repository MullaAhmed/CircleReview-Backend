from django.conf import settings
from Employee.models import *
from django.core.mail import send_mail
from .models import *
from .serializers import *
from Employee.serializers import *
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

def create_feedback(og_data,id):
    
    for i in og_data['people']:
        data={
            "employee_name":i,
            "company_name":og_data['company_name'],
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

            "self_review":og_data['self_review'],
            "peer_review":og_data['peer_review'],
            "manager_review":og_data['manager_review'],
            "hr_review":og_data['hr_review'],
            "external_review":og_data['external_review']
        }
    
        serializer = FeedbackSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            update_userprofile(og_data['people'],"self_review","Pending")

            print("done")
        else:
            print(serializer.errors)
        

def update_userprofile(people,review_type,status):
    for i in people:
        user=UserProfile.objects.get(id=int(i))
        user.review_status[review_type]=status
        serializer=UserProfileSerializer(user,data=user)
        if serializer.is_valid():
            serializer.save()
        