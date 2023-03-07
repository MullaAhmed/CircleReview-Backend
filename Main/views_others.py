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
    lookup_form_id=('form_id')
    lookup_form_type=('review_type')
    def get(self,request, *args, **kwargs):
        if not isinstance(request.auth_details, AuthDetails):
            return response.Response({"error": "no auth details found"}, status=401)
        else:
            form_id=self.kwargs.get(self.lookup_form_id)
            feedback_type=self.kwargs.get(self.lookup_form_type)
            form=Feedback.objects.filter(form_id=form_id,feedback_type=feedback_type)
            
            serializer = FeedbackSerializer(form,many=True)

            resp=HttpResponse(content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename="{}-{}.csv"'.format(serializer.data[0]["form_id"],serializer.data[0]["company_name"])
    

            writer=csv.writer(resp)

            headings=['Id','User From','User For','Feedback Type','Company Name']
            
            headings.extend([x['question'] for x in (serializer.data[0]['questions_answers'])])
            print(headings)
            writer.writerow(headings)
            for data in serializer.data:
                row=[]
                row.append(data['id'])
                row.append(data['user_from'])
                row.append(data['user_for'])
                row.append(data['feedback_type'])
                row.append(data['company_name']) 
                try:
                    row.extend([x['answer'] for x in (data['questions_answers'])])
                except:
                    pass

                writer.writerow(row)
            
            return resp
