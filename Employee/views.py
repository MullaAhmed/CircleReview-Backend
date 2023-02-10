from django.shortcuts import render
from rest_framework import response,mixins,generics
from rest_framework.views import APIView
from .models import *
from .serializers import *
import pandas as pd
from cohesive.auth import AuthDetails
from django.db.models import Q # Multi crteria queries
# Create your views here.

class UserProfileView(APIView):
    lookup_field = 'profile'

    def get(self,request, *args, **kwargs):
        
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            profile=self.kwargs.get(self.lookup_field)
            
            if str(profile).lower()=="me":
                queryset = UserProfile.objects.filter(name=str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", "")).first()    
                serializer = UserProfileSerializer(queryset)
                return response.Response(serializer.data)
            
            else:
                user=UserProfile.objects.filter(company_name=str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id))
                serializer=UserProfileSerializer(user,many=True)
                return response.Response(serializer.data,status=200)

    def post(self,request,*args, **kwargs):
        
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            data={
                "email":request.auth_details["user_email"],
                "name":str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", ""),
                "company_name":str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id),
                "position":request.data["position"],
               

                "cohesieve_role":request.auth_details.role,
                "cohesieve_user_id":request.auth_details.user_id,
                "cohesieve_user_name":request.auth_details.user_name,
                "cohesieve_workspace_id":request.auth_details.workspace_id,
                "cohesieve_workspace_name":request.auth_details.workspace_name,
                
               
                "related_people":{
                            "peer":[],
                            "manager":[],
                            "hr_review":[],
                            "external":[] 
                },
                "review_status":{
                            "self_review":"Pending",
                            "peer_review":"Pending",
                            "manager_review":"Pending",
                            "hr_review":"Pending",
                            "external_review":"Pending"
                },
                "nominations": {
                            "peer_review": [],
                            "manager_review": [],
                            "hr_review": [],
                            "external_review": []
                }
                }


            serializer=UserProfileSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data,status=200)
            return response.Response(serializer.errors,status=401)

    
    def put(self,request,*args, **kwargs):
        lookup_field = 'profile'
        
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            profile=self.kwargs.get(self.lookup_field)
            if str(profile).lower()=="me":
                user = UserProfile.objects.filter(name=str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", "")).first()        
                serializer=UserProfileSerializer(user,data=request.data,partial=True)
                
                if serializer.is_valid():
                    
                    serializer.save()
                    return response.Response(serializer.data,status=200)
                return response.Response(serializer.errors,status=400)
            else:
                user = UserProfile.objects.filter(name=profile).first()
                serializer=UserProfileSerializer(user,data=request.data,partial=True)
                
                if serializer.is_valid():
                    
                    serializer.save()
                    return response.Response(serializer.data,status=200)
                return response.Response(serializer.errors,status=400)
            


class CSVtoUserProfile(APIView):
    def post(self,request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            file=request.data['file']
            data=pd.read_csv(file)
            for i in range(data.shape[0]):
                row=(data.iloc[i,:]).values
                data={
                    "email":row[0],
                    "name":row[1],
                    "company_name":row[2],
                    "position":row[3],
                

                    "cohesieve_role":row[4],
                    "cohesieve_user_id":row[5],
                    "cohesieve_user_name":row[6],
                    "cohesieve_workspace_id":row[7],
                    "cohesieve_workspace_name":row[8],
                    
                
                    "related_people":{
                                "peer":[],
                                "manager":[],
                                "hr_review":[],
                                "external":[] 
                    },
                    "review_status":{
                                "self_review":"Pending",
                                "peer_review":"Pending",
                                "manager_review":"Pending",
                                "hr_review":"Pending",
                                "external_review":"Pending"
                    },
                    "nominations": {
                                "peer_review": [],
                                "manager_review": [],
                                "hr_review": [],
                                "external_review": []
                    }
                    }
                serializer=UserProfileSerializer(data=data)
                if serializer.is_valid():
                    
                    serializer.save()
                    return response.Response(serializer.data,status=200)
                else:
                    return response.Response(serializer.errors,status=400)               
            