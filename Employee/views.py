from django.shortcuts import render
from rest_framework import response,mixins,generics
from rest_framework.views import APIView
from .models import *
from .serializers import *
import pandas as pd
from django.db.models import Q # Multi crteria queries
# Create your views here.

class UserProfileView(APIView):
    lookup_id = 'id'
    lookup_company = 'company' 

    def get(self, *args, **kwargs):
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
        serializer=UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data,status=200)
        return response.Response(serializer.errors,status=401)

    def put(self,request,*args, **kwargs):
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

    def get(self,*args, **kwargs):
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
        serializer=TeamSerializer(data=request.data)
        
        if serializer.is_valid():
            
            serializer.save()
            return response.Response(serializer.data,status=200)
        return response.Response(serializer.errors,status=400)


class CSVtoUserProfile(APIView):
    def post(self,request,*args, **kwargs):
        file=request.data['file']
        data=pd.read_csv(file)
        for i in range(data.shape[0]):
            row=(data.iloc[i,:]).values
            data={
                "user":row[0],
                "email":row[1],
                "name":row[2],
                "team_name":row[3],
                "dept_name":row[4],
                "position":row[5],
                "review_status":{
                                "self_review":"Not assigned",
                                "peer_review":"Not assigned",
                                "manager_review":"Not assigned",
                                "hr_review":"Not assigned",
                                "external_review":"Not assigned"
                                },
                "nominations":{}
            }
    

            serializer=UserProfileSerializer(data=data)
            if serializer.is_valid():
                print(serializer.validated_data)
                serializer.save()
                
        return response.Response("done")