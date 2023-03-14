from django.urls import path
from .views_feedback import *
from .views_feedback_form import *
from .views_user_profile import *
from .views_others import *

urlpatterns = [
    path('userprofile/<slug:profile>/',UserProfileView.as_view()),
    path('userrelation/<slug:relation>/',UserRelationView.as_view()),
    path('csvtouserprofile/',CSVtoUserProfileView.as_view()),
   
    path('feedbackform/',FeedbackFormView.as_view()),
    path('feedbackform/<int:form_id>/',FeedbackDetailFormView.as_view()),
    path('feedbackform/<int:form_id>/clone/',CloneFeedbackFormView.as_view()),
    path('feedback/all/<int:form_id>/',FeedbackView.as_view()),
    # path('feedback/',UserFeedbackView.as_view()),
    path('feedback/<int:feedback_id>/',EditFeedbackView.as_view()),

    path('remainder-emails/',RemainderEmailView.as_view()),
    path('report/<int:form_id>/<slug:review_type>/',ReportView.as_view())
    ]