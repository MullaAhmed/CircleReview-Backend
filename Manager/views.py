from django.shortcuts import render
from rest_framework import response,mixins
from rest_framework.views import APIView
from rest_framework.generics import *
from .models import *
from .serializers import *
from .utilities import *
import csv
from Employee.serializers import *
from django.http import HttpResponse
from django.db.models import Q # Multi crteria queries
from cohesive.auth import AuthDetails
# Create your views here.

class FeedbackFormView(APIView):  

    def post(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            if str(request.auth_details.role).lower()=="hr":

                data={   

        "survey_name":request.data['survey_name'],
        "company_name":str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id),
        
        "status":request.data['status'],
        "people":request.data['people'],
        "completion_rate":0,
        
        "self_review":request.data['self_review'],
        "peer_review":request.data['peer_review'],
        "manager_review":request.data['manager_review'],
        "hr_review":request.data['hr_review'],
        "external_review":request.data['external_review'],

}
                
                serializer = FeedbackFormSerializer(data=data)
                
                if serializer.is_valid():            
                    
                    obj=serializer.save()
                    
                    create_feedback(data,obj.id) #later async
                    send_email_team(data['people']) #later async

                    return response.Response(serializer.data,status=200)
                else:
                    return response.Response(serializer.errors,status=401)

    
    def get(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            role=str(request.auth_details.role).lower()
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)
           
            if str(role)=="hr":
                queryset = FeedbackForm.objects.filter(Q(company_name=company))
                serializer = FeedbackFormSerializer(queryset,many=True)
                return response.Response(serializer.data,status=200)
            else:   
                return response.Response({"message":"You dont have access"},status=401)



class FeedbackDetailFormView(APIView):
    lookup_field=('form_id')
    def get(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_field)
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)
            queryset = FeedbackForm.objects.get(Q(company_name=company) & Q(id=id))
            serializer = FeedbackFormSerializer(queryset)
            return response.Response(serializer.data,status=200)
    
    def put(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_field)
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)
            queryset = FeedbackForm.objects.get(Q(company_name=company) & Q(id=id))
            serializer = FeedbackFormSerializer(queryset,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data,status=200)
            else:
                return response.Response(serializer.errors,status=401)


class CloneFeedbackFormView(APIView):
    lookup_field=('form_id')
    

    def post(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            if str(request.auth_details.role).lower()=="hr":
                id=self.kwargs.get(self.lookup_field)
                company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)

                queryset= FeedbackForm.objects.get(Q(company_name=company) & Q(id=id) & Q(status="Active"))
                serializer = FeedbackFormSerializer(queryset)
                save_serializer = FeedbackFormSerializer(data=dict(serializer.data))
                if save_serializer.is_valid():
                    save_serializer.save()
                    return response.Response({"message":"successfully cloned"},status=200)
                else:
                    return response.Response(serializer.errors,status=401)
            else:
                return response.Response({"message":"You dont have access"},status=401)
    

class FeedbackView(APIView):
    lookup_field=('form_id')
    def get(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            role=str(request.auth_details.role).lower()
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)
            id=self.kwargs.get(self.lookup_field)

            if str(role)=="hr":
                queryset = Feedback.objects.filter(Q(company_name=company) & Q(feedback_form=id))
                serializer = FeedbackSerializer(queryset,many=True)
                return response.Response(serializer.data,status=200)
            elif str(role)=="manager":
                manager_name= str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", "")
                queryset = Feedback.objects.filter(Q(company_name=company) & Q(manager_name=manager_name) & Q(feedback_form=id))
                serializer = FeedbackSerializer(queryset)
                return response.Response(serializer.data,status=401)
            

class NominationsView(APIView):
    lookup_id=('feedback_id')
    
    def put(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_id)
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)

            # check nomination with the logged in user
            form=Feedback.objects.get(Q(company_name=company) & Q(id=id))  
            data=request.data

            nominations=['peer_review','manager_review','hr_review','external_review']
            
            serializer = FeedbackSerializer(form,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                
                for u in nominations:
                    user=UserProfile.objects.filter(id=int(data['nominations'][u]))
                    temp=dict(user.values()[0])
                    temp['nominations'][u].append(serializer.data['employee_name'])
                    print(temp['nominations'])
                    temp_Serializer=UserProfileSerializer(user[0],data=temp,partial=True)
                    if temp_Serializer.is_valid():
                        print("yess")
                        temp_Serializer.save()
                    else:
                        return response.Response(temp_Serializer.errors,status=401)
                
                
                return response.Response(serializer.data,status=200)
            else:
                return response.Response(serializer.errors,status=401)


class EditFeedbackView(APIView):
    lookup_id=('feedback_id')

    def get(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            
            id=int(self.kwargs.get(self.lookup_id))
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)
            queryset=Feedback.objects.get(Q(company_name=company) & Q(id=id))
            serializer = FeedbackSerializer(queryset)

            if (str(request.auth_details.role).lower()=="hr" 
                or (dict(serializer.data)["manager_name"])==UserProfile.objects.filter(id=id).values()["manager_name"] 
                or dict(serializer.data)["employee_name"]==str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", "")):
                return response.Response(serializer.data,status=200)
            else:
                return response.Response({"message":"You dont have access"},status=401)

    def put(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_id)
            review_type=self.kwargs.get('type')
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)
            
            
            data=request.data

            # check nomination with the logged in user
            form=Feedback.objects.get(Q(company_name=company) & Q(id=id))     
        
            data["status"]=form.status
            data["status"][review_type]="Completed"
            
            feedback_form=FeedbackForm.objects.filter(id=form.feedback_form)
        
            completion_rate=feedback_form[0].completion_rate+(1/(4*len(feedback_form[0].people.all())))
            temp=dict(feedback_form.values()[0])
            temp['completion_rate']=completion_rate
            
            feedback_form_serializer=FeedbackFormSerializer(data=temp,partial=True)
            
            if feedback_form_serializer.is_valid():
                feedback_form_serializer.save()

            serializer = FeedbackSerializer(form,data=request.data,partial=True)
            if serializer.is_valid():

                serializer.save()
                return response.Response(serializer.data,status=200)
            else:
                return response.Response(serializer.errors,status=401)


class RemainderEmailView(APIView):
    lookup_field=('id')

    def post(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_field)
            form=FeedbackForm.objects.get(id=id)
            feedback=Feedback.objects.get(feedback_form=id)
            team_lead=UserProfile.objects.get(name=feedback.manager_name)
            serializers = FeedbackFormSerializer(form)
            send_remainder_emails(serializers.data['people'],team_lead.email)
            
            return response.Response({"message":"successfully sent"},status=200)


class ReportView(APIView):
    lookup_field=('id')

    def get(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_field)
            form=Feedback.objects.filter(feedback_form=id)
            
            serializer = FeedbackSerializer(form,many=True)

            resp=HttpResponse(content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename="{}-{}.csv"'.format(serializer.data[0]["feedback_form"],serializer.data[0]["company_name"])
    

            writer=csv.writer(resp)

            headings=['id','employee_name','feedback_form','company_name']
            headings.extend([ "status_"+str(x) for x in list(dict(serializer.data[0]['status']).keys())])
            headings.extend([ "nominee_"+str(x) for x in list(dict(serializer.data[0]['nominations']).keys())])
            headings.extend([x['question'] for x in (serializer.data[0]['self_review']["questions"])])
            headings.extend([x['question'] for x in (serializer.data[0]['peer_review']["questions"])])
            headings.extend([x['question'] for x in (serializer.data[0]['manager_review']["questions"])])
            headings.extend([x['question'] for x in (serializer.data[0]['hr_review']["questions"])])
            headings.extend([x['question'] for x in (serializer.data[0]['external_review']["questions"])])

            writer.writerow(headings)
            for data in serializer.data:
                row=[]
                row.append(data['id'])
                row.append(data['employee_name'])
                row.append(data['feedback_form'])
                row.append(data['company_name'])
                row.extend(list(dict(data['status']).values()))
                row.extend(list(dict(data['nominations']).values()))
                try:
                    row.extend([x['answer'] for x in (data['self_review']["questions"])])
                except:
                    pass
                try:
                    row.extend([x['answer'] for x in (data['peer_review']["questions"])])
                except:
                    pass
                try:
                    row.extend([x['answer'] for x in (data['manager_review']["questions"])])
                except:
                    pass
                try:
                    row.extend([x['answer'] for x in (data['hr_review']["questions"])])
                except:
                    pass
                try:
                    row.extend([x['answer'] for x in (data['external_review']["questions"])])
                except:
                    pass
            
                writer.writerow(row)
            
            return resp

class GenerateCSVView(APIView):
    

    def get(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:  
            try:
                resp=HttpResponse(content_type='text/csv')
                print(request.data[0]["feedback_form"])
                resp['Content-Disposition'] = 'attachment; filename="{}-{}.csv"'.format(request.data[0]["feedback_form"],request.data[0]["company_name"])
        

                writer=csv.writer(resp)

                headings=['id','employee_name','feedback_form','company_name']
                headings.extend([ "status_"+str(x) for x in list(dict(request.data[0]['status']).keys())])
                headings.extend([ "nominee_"+str(x) for x in list(dict(request.data[0]['nominations']).keys())])
                headings.extend([x['question'] for x in (request.data[0]['self_review']["questions"])])
                headings.extend([x['question'] for x in (request.data[0]['peer_review']["questions"])])
                headings.extend([x['question'] for x in (request.data[0]['manager_review']["questions"])])
                headings.extend([x['question'] for x in (request.data[0]['hr_review']["questions"])])
                headings.extend([x['question'] for x in (request.data[0]['external_review']["questions"])])

                writer.writerow(headings)
                for data in request.data:
                    row=[]
                    row.append(data['id'])
                    row.append(data['employee_name'])
                    row.append(data['feedback_form'])
                    row.append(data['company_name'])
                    row.extend(list(dict(data['status']).values()))
                    row.extend(list(dict(data['nominations']).values()))
                    
                    try:
                        row.extend([x['answer'] for x in (data['self_review']["questions"])])
                    except:
                        pass
                    try:
                        row.extend([x['answer'] for x in (data['peer_review']["questions"])])
                    except:
                        pass
                    try:
                        row.extend([x['answer'] for x in (data['manager_review']["questions"])])
                    except:
                        pass
                    try:
                        row.extend([x['answer'] for x in (data['hr_review']["questions"])])
                    except:
                        pass
                    try:
                        row.extend([x['answer'] for x in (data['external_review']["questions"])])
                    except:
                        pass
                    writer.writerow(row)
                
                return resp
            
            except:    
                return response.Response({"message":"no data"},status=401)



class ManagerView(APIView):
    lookup_field=('name')
    def get(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            name=self.kwargs.get(self.lookup_field)
            queryset= Team.objects.filter(team_lead=name)
            team_members=queryset[0].team_members
            data=[]
            for i in (list(team_members.all())):
                user_id=i.id
                feedback=Feedback.objects.filter(employee_name=i)         
                serializer=FeedbackSerializer(feedback[0])
                data.append(serializer.data)
            

            print(data)
            
            
            return response.Response(data,status=200)