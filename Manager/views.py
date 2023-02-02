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
# Charts
# import xlwings as xw
# import xlwt
# import pandas as pd
# import matplotlib.pyplot as plt  # pip install matplotlib



# Create your views here.

class FeedbackFormView(APIView,mixins.UpdateModelMixin):
    lookup_id=('id')
    lookup_company=('company')

    def get(self, *args, **kwargs):
        id=self.kwargs.get(self.lookup_id)
        company=self.kwargs.get(self.lookup_company)

        if id==0:
            queryset = FeedbackForm.objects.filter(Q(company_name=company) & Q(status="Active"))
            serializer = FeedbackFormSerializer(queryset,many=True)
            return response.Response(serializer.data,status=200)
        else:
            queryset= FeedbackForm.objects.get(Q(company_name=company) & Q(id=id) & Q(status="Active"))
            serializer = FeedbackFormSerializer(queryset)
            return response.Response(serializer.data,status=401)

    def post(self,request, *args, **kwargs):
        data=request.data
        
        serializer = FeedbackFormSerializer(data=data)
        
        if serializer.is_valid():            
            
            obj=serializer.save()
            
            create_feedback(data,obj.id) #later async
            send_email_team(data['people']) #later async

            return response.Response(serializer.data,status=200)
        else:
            return response.Response(serializer.errors,status=401)


    def put(self, request, *args, **kwargs):
        id=self.kwargs.get(self.lookup_id)
        company=self.kwargs.get(self.lookup_company)
        form=FeedbackForm.objects.get(Q(company_name=company) & Q(id=id))
        serializer = FeedbackFormSerializer(form,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            
            return response.Response(serializer.data,status=200)
        else:
            return response.Response(serializer.errors,status=401)


class FeedbackView(APIView):
    lookup_id=('id')
    def get(self, request,*args, **kwargs):
        id=self.kwargs.get(self.lookup_id)
        if id==0:
            queryset = Feedback.objects.all()
            serializer = FeedbackSerializer(queryset,many=True)
            return response.Response(serializer.data,status=200)
        else:
            queryset= Feedback.objects.get(id=id)
            serializer = FeedbackSerializer(queryset)
            return response.Response(serializer.data,status=401)
        

class NominationsView(APIView):
    lookup_id=('id')
    lookup_company=('company')
        

    def put(self,request, *args, **kwargs):
        id=self.kwargs.get(self.lookup_id)
        company=self.kwargs.get(self.lookup_company)

        # check nomination with the logged in user
        form=Feedback.objects.get(Q(company_name=company) & Q(id=id))  
        data=request.data

        nominations=['peer_review','manager_review','hr_review','external_review']
           
        serializer = FeedbackSerializer(form,data=request.data,partial=True)
        if serializer.is_valid():

            # serializer.save()
            for u in nominations:
                user=UserProfile.objects.filter(id=int(data['nominations'][u]))
                temp=dict(user.values()[0])
                temp['nominations'][u]=serializer.data['employee_name']
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
    lookup_id=('id')
    lookup_company=('company')

    def get(self, request,*args, **kwargs):
        id=int(self.kwargs.get(self.lookup_id))
        company=self.kwargs.get(self.lookup_company)
        review_type=self.kwargs.get('type')
        queryset=Feedback.objects.get(Q(company_name=company) & Q(id=id))
        
        
        serializer = FeedbackSerializer(queryset)
        return response.Response(serializer.data[review_type],status=200)
        

    def put(self,request, *args, **kwargs):
        id=self.kwargs.get(self.lookup_id)
        company=self.kwargs.get(self.lookup_company)
        review_type=self.kwargs.get('type')
        
        data=request.data

        # check nomination with the logged in user
        form=Feedback.objects.get(Q(company_name=company) & Q(id=id))     
    
        data["status"]=form.status
        data["status"][review_type]="Completed"
           
        serializer = FeedbackSerializer(form,data=request.data,partial=True)
        if serializer.is_valid():

            serializer.save()
            return response.Response(serializer.data,status=200)
        else:
            return response.Response(serializer.errors,status=401)


class RemainderEmailView(APIView):
    lookup_field=('id')

    def post(self,request, *args, **kwargs):
        id=self.kwargs.get(self.lookup_field)
        form=FeedbackForm.objects.get(id=id)
        team=Team.objects.get(team_name=form.team)
        team_lead=UserProfile.objects.get(user=team.team_lead)
        serializers = FeedbackFormSerializer(form)
        send_remainder_emails(serializers.data['people'],team_lead.email)
        
        return response.Response({"message":"successfully sent"},status=200)
        

class ReportView(APIView):
    lookup_field=('id')

    def get(self,request, *args, **kwargs):
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
            row.extend([x['answer'] for x in (data['self_review']["questions"])])
            row.extend([x['answer'] for x in (data['peer_review']["questions"])])
            row.extend([x['answer'] for x in (data['manager_review']["questions"])])
            row.extend([x['answer'] for x in (data['hr_review']["questions"])])
            row.extend([x['answer'] for x in (data['external_review']["questions"])])
            writer.writerow(row)
        
        return resp
