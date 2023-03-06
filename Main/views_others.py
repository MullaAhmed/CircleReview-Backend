from rest_framework import response,mixins
from rest_framework.views import APIView
from rest_framework.generics import *
from .models import *
from .serializers import *
from .utilities import *
import csv

from django.http import HttpResponse
from django.db.models import Q # Multi crteria queries
from cohesive.auth import AuthDetails

class RemainderEmailView(APIView):
    lookup_field=('id')

    def post(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            id=self.kwargs.get(self.lookup_field)
            form=FeedbackForm.objects.get(id=id)
            serializers = FeedbackFormSerializer(form)
            send_remainder_emails(serializers.data['people'])
            
            return response.Response({"message":"successfully sent"},status=200)

class ReportView(APIView):
    lookup_field=('id')

    def get(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
           pass