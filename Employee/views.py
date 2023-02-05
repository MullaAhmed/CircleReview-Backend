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
    lookup_id = 'id'
    lookup_company = 'company' 

    def get(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_id)
            company=self.kwargs.get(self.lookup_company)
            if id==0:
                queryset = UserProfile.objects.filter(company_name=company)
                serializer = UserProfileSerializer(queryset,many=True)
                return response.Response(serializer.data)
            else:
                user=UserProfile.objects.get(Q(id=id) & Q(company_name=company))
                serializer=UserProfileSerializer(user)
                return response.Response(serializer.data,status=200)

    def post(self,request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            serializer=UserProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data,status=200)
            return response.Response(serializer.errors,status=401)

    def put(self,request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_id)
            company=self.kwargs.get(self.lookup_company)
            user=UserProfile.objects.get(Q(id=id) & Q(company_name=company))
            
            serializer=UserProfileSerializer(user,data=request.data,partial=True)
            
            if serializer.is_valid():
                print(dict(serializer.validated_data))
                serializer.save()
                return response.Response(serializer.data,status=200)
            return response.Response(serializer.errors,status=400)


class TeamView(APIView):
    lookup_id="id"
    lookup_company="company"

    def get(self,request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_id)
            company=self.kwargs.get(self.lookup_company)

            if id==0:
                queryset = Team.objects.filter(company_name=company)
                serializer = TeamSerializer(queryset,many=True)
                return response.Response(serializer.data)
            else:
                user=Team.objects.get(Q(id=id) & Q(company_name=company))
                serializer=TeamSerializer(user)
                return response.Response(serializer.data,status=200)

    def post(self,request,*args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            serializer=TeamSerializer(data=request.data)
            
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
                    "user":row[0],
                    "email":row[1],
                    "company_name":row[10],
                    "name":row[2],
                    "team_name":row[3],
                    "dept_name":row[4],
                    "position":row[5],
                    "review_status":{
                                    "self_review":"Pending",
                                    "peer_review":"Pending",
                                    "manager_review":"Pending",
                                    "hr_review":"Pending",
                                    "external_review":"Pending",
                },
                    "related_people":{
                                    "peer_review":[UserProfile.objects.filter(email=str(i).strip())[0].id if UserProfile.objects.filter(email=str(i).strip()).exists() else 'ahmed.mce20@sot.pdpu.ac.in' for i in row[6].split(",")],
                                    "manager_review":[UserProfile.objects.filter(email=row[7])[0].id],
                                    "hr_review":[UserProfile.objects.filter(email=row[8])[0].id],
                                    "external_review":[UserProfile.objects.filter(email=str(i).strip())[0].id if UserProfile.objects.filter(email=str(i).strip()).exists() else 'ahmed.mce20@sot.pdpu.ac.in' for i in row[9].split(",")]
                                    },
                    "nominations":{
                                    "peer_review": [],
                                    "manager_review": [],
                                    "hr_review": [],
                                    "external_review": []
                    }
                }
                # print([UserProfile.objects.filter(email=x.strip()).exists() for x in row[6].split(",")])

                serializer=UserProfileSerializer(data=data)
                if serializer.is_valid():
                    
                    serializer.save()
                    return response.Response(serializer.data,status=200)
                else:
                    return response.Response(serializer.errors,status=400)               
            