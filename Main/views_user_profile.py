from rest_framework import response,mixins,generics
from rest_framework.views import APIView
from .models import *
from .serializers import *
import pandas as pd
from cohesive.auth import AuthDetails
from django.db.models import Q # Multi crteria queries
from .utilities import *

# Create your views here.

class UserProfileView(APIView):
    lookup_field = 'profile'
    def get(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            profile=self.kwargs.get(self.lookup_field)

            if str(profile).lower()=="me":
                queryset = UserProfile.objects.filter(employee_id=str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", "")).first()    
                serializer = UserProfileSerializer(queryset)
                return response.Response(serializer.data)
            
            elif str(profile).lower()=="all":
                user=UserProfile.objects.filter(cohesieve_workspace_id=str(request.auth_details.workspace_id)).all()
                serializer=UserProfileSerializer(user,many=True)
                return response.Response(serializer.data,status=200)
            
            else:
                user=UserProfile.objects.filter(id=profile).first()
                serializer=UserProfileSerializer(user)
                return response.Response(serializer.data,status=200)


    def post(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            data={
                "email":request.auth_details.user_email,
                "employee_id":str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", ""),
                "company_name":str(request.auth_details.workspace_name)+"_"+str(request.auth_details.workspace_id),
                "position":request.data["position"],
                "manager":Try_Except.get_manager(request.data["manager"]),

                "name":request.data["name"],
                "dob":request.data["dob"],
                "phone_number":request.data["phone_number"],
                "doj":request.data["doj"],


                "cohesieve_role":request.auth_details.role,
                "cohesieve_user_id":request.auth_details.user_id,
                "cohesieve_user_name":request.auth_details.user_name,
                "cohesieve_workspace_id":request.auth_details.workspace_id,
                "cohesieve_workspace_name":request.auth_details.workspace_name,
                
                }
            
            serializer=UserProfileSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                add_user_relations(data["employee_id"])
                
                return response.Response(serializer.data,status=200)
            return response.Response(serializer.errors,status=401)

    def put(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            if str(request.auth_details.role).lower()=="hr":
                profile=self.kwargs.get(self.lookup_field)
                user=UserProfile.objects.filter(id=profile).first()
                serializer=UserProfileSerializer(user,data=request.data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return response.Response(serializer.data,status=200)
                return response.Response(serializer.errors,status=401)

class UserRelationView(APIView):
    lookup_field = 'relation'
    def get(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            user_1= UserProfile.objects.filter(employee_id=str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", "")).first()    
            relation=self.kwargs.get(self.lookup_field).lower()
            if str(relation).lower()=="all":
                users=UserRelation.objects.filter(user_1=user_1).all()
                serializer=UserRelationSerializer(users,many=True)
                return response.Response(serializer.data,status=200)
            else:
                users=UserRelation.objects.filter(Q(user_1=user_1) | Q(relation=relation)).all()
                serializer=UserRelationSerializer(users,many=True)
                return response.Response(serializer.data,status=200)
    
    def post(self, request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            user_1= UserProfile.objects.filter(employee_id=str(request.auth_details.user_id)+"_"+str(request.auth_details.user_name).replace(" ", "")).first()    
            user_2=UserProfile.objects.filter(id=request.data["user_2"]).first()
            relation=request.data["relation"]
            data={
                "user_1":user_1,
                "user_2":user_2.id,
                "relation":relation,
            }
            serializer=UserRelationSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data,status=200)
            return response.Response(serializer.errors,status=401)

class CSVtoUserProfileView(APIView):
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
                    "employee_id":row[1],
                    "company_name":row[2],
                    "position":row[3],
                    "manager":str(row[4]),

                    "name":row[5],
                    "dob":row[6],
                    "phone_number":row[7],
                    "doj":row[8],


                    "cohesieve_role":row[9],
                    "cohesieve_user_id":row[10],
                    "cohesieve_user_name":row[11],
                    "cohesieve_workspace_id":row[12],
                    "cohesieve_workspace_name":row[13],
                    
                    }
                serializer=UserProfileSerializer(data=data)
                # print(data)
                if serializer.is_valid():
                
                    serializer.save()
                    return response.Response(serializer.data,status=200)
                else:
                    return response.Response(serializer.errors,status=400)               
            
##############################################