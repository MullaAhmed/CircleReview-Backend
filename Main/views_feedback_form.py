from rest_framework import response,mixins,generics
from rest_framework.views import APIView
from .models import *
from .serializers import *
import pandas as pd
from cohesive.auth import AuthDetails
from django.db.models import Q # Multi crteria queries
from .utilities import *

# Create your views here.

class FeedbackFormView(APIView):
    def post(self,request, *args, **kwargs):
       
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            
                role=str(request.auth_details.role).lower() 
                print(role)
                data={   

                    "survey_name":request.data['survey_name'],
                    "company_name":str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id),
                    
                    "status":request.data['status'],
                    "people":request.data['people'],
                    "completion_rate":0,
                    
                    "self_review":request.data['self_review'],
                    "peer_review":request.data['peer_review'],
                    "manager_review":request.data['manager_review'],
                    "direct_report_review":request.data['direct_report_review'],
                    # "cross_functional_review":request.data['cross_functional_review'],

            }
                
                serializer = FeedbackFormSerializer(data=data)
                
                if serializer.is_valid():            
                    
                    obj=serializer.save()
                    create_feedback(data,obj.id) # async
                    
                    return response.Response(serializer.data,status=200)
                else:
                    return response.Response(serializer.errors,status=401)

    
    def get(self, request,*args, **kwargs):
        
        if not isinstance(request.auth_details, AuthDetails):
            
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            role=str(request.auth_details.role).lower()
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)
            print(role)
            if str(role)=="hr":
                
                queryset = FeedbackForm.objects.filter(Q(company_name=company))
                serializer = FeedbackFormSerializer(queryset,many=True)
                print(serializer.data)
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
            serializer = FeedbackFormSerializer(queryset,data=request.data,partial=True)
            if serializer.is_valid():
                obj=serializer.save()
                create_feedback(dict(serializer.data),obj.id) 
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

                queryset= FeedbackForm.objects.get(Q(company_name=company) & Q(id=id))
                serializer = FeedbackFormSerializer(queryset)
                save_serializer = FeedbackFormSerializer(data=dict(serializer.data))
                if save_serializer.is_valid():
                    obj=save_serializer.save()
                    
                    return response.Response({"message":"successfully cloned"},status=200)
                else:
                    return response.Response(serializer.errors,status=401)
            else:
                return response.Response({"message":"You dont have access"},status=401)
    

