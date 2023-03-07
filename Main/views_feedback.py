from rest_framework import response,mixins,generics
from rest_framework.views import APIView
from .models import *
from .serializers import *
import pandas as pd
from cohesive.auth import AuthDetails
from django.db.models import Q # Multi crteria queries
from .utilities import *

# Create your views here.

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
                queryset = Feedback.objects.filter(Q(company_name=company) & Q(form_id=id))
                serializer = FeedbackSerializer(queryset,many=True)
                return response.Response(serializer.data,status=200)
            

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
                or dict(serializer.data)["user_from"]==(UserProfile.objects.get(email=request.auth_details.user_email).id)):
                return response.Response(serializer.data,status=200)
            else:
                return response.Response({"message":"You dont have access"},status=401)

    def put(self,request,*args,**kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=int(self.kwargs.get(self.lookup_id))
            company=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id)
            queryset=Feedback.objects.get(Q(company_name=company) & Q(id=id))
            serializer = FeedbackSerializer(queryset,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                update_completion_rate(serializer.data["form_id"])
                return response.Response(serializer.data,status=200)
            else:
                return response.Response(serializer.errors,status=401)