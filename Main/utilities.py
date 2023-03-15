from .models import *
from .serializers import *
from django.db.models import Q # Multi crteria queries
from django.conf import settings
from django.core.mail import send_mail
# def update_user_relations(user_id):

def add_user_relations(user_1_id):
    user_1=UserProfile.objects.filter(employee_id=user_1_id).first()
    manager_id=user_1.manager
    if manager_id!="None":
        # Peers
        peers_list=[]
        peers=UserProfile.objects.filter(manager=manager_id).all()
        if len(peers)>=2:
            print(peers)
            for peer in peers:
                if peer.id!=user_1.id:
                    data=UserRelation(
                        user_1=user_1,
                        user_2=peer.id,
                        relation="peer")
                    peers_list.append(data)

            UserRelation.objects.bulk_create(peers_list)
            
def send_remainder_emails(people): 
    recipient_list = []
    for i in people:
        print(i)
        subject = 'Review Survey'
        person=UserProfile.objects.get(id=int(i))
        recipient_list.append(person.email)
        
    message = f'Hi, the review survey is out. Please visit <link> and fill your self review and review for your peers.'
    email_from = settings.EMAIL_HOST_USER
    
    send_mail( subject, message, email_from, recipient_list ) 
  
def send_email_team(person_id):
    
        subject = 'Review Survey'
        person=UserProfile.objects.get(id=int(person_id))
        
        message = f'Hi {person.name}, the review survey is out. Please visit <link> and fill yours'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [person.email, ]
        send_mail( subject, message, email_from, recipient_list )

def update_completion_rate(id):
    all_feedbacks=Feedback.objects.filter(form_id=id).count()
    completed_feedbacks=Feedback.objects.filter(Q(form_id=id) & Q(status="Completed")).count()
    feedback_form=FeedbackForm.objects.get(id=id)
    feedback_form.completion_rate=(int(completed_feedbacks)/int(all_feedbacks))*100
    serializer=FeedbackFormSerializer(feedback_form,data=feedback_form.__dict__)
    if serializer.is_valid():
        serializer.save()

class Try_Except:
    def get_manager(manager_id):
        try:
            return UserProfile.objects.filter(id=manager_id).first().id
        except:
            return "None"
    
    def get_peers(user_id,people_list):
        try:
            all_peers=UserRelation.objects.filter(user_1=user_id,relation="peer").all()
            final=[x for x in all_peers if x.id in people_list]
            
        except:
            final= []
        return final
   

    
    def get_direct_reports(user_id,people_list):
        try:
            all_direct_reports=UserProfile.objects.filter(manager=user_id).all()
        
            final=[x for x in all_direct_reports if x.id in people_list]
        except:
            final= []
        return final


def create_feedback(og_data,id):
    people=og_data["people"]
    relations=[]
    company_name=og_data["company_name"]
    form_name=og_data["survey_name"]
    for p in people:
        
        person=UserProfile.objects.get(id=int(p))

        
        peers=Try_Except.get_peers(person.id,people)
        for peer in peers:
            data=Feedback(user_from=peer.id,user_for=person.id,feedback_type="peer",company_name=company_name,form_id=id,form_name=form_name,questions_answers=og_data["peer_review"]["questions"])
            if data not in relations:
                relations.append(data)
        
       
        direct_reports=Try_Except.get_direct_reports(person.id,people)
        for direct in direct_reports:
            data=Feedback(user_from=person.id,user_for=direct.id,feedback_type="direct_report",company_name=company_name,form_id=id,form_name=form_name,questions_answers=og_data["direct_report_review"]["questions"])
            if data not in relations:
                relations.append(data)
        manager=Try_Except.get_manager(person.manager)
        if manager!="None" and manager in people: 
            data=Feedback(user_from=person.id,user_for=manager,feedback_type="manager",company_name=company_name,form_id=id,form_name=form_name,questions_answers=og_data["manager_review"]["questions"])
            if data not in relations:
                relations.append(data)
        
    Feedback.objects.bulk_create(relations)
        