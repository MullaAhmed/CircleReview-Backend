from django.urls import path,include
from . import views


urlpatterns = [
    
    path('feedbackform/<slug:company>/<int:id>/',views.FeedbackFormView.as_view()),
    path('feedback/<slug:company>/<slug:id>/<slug:type>/',views.EditFeedbackView.as_view()),
    path('r-email/<int:id>/',views.RemainderEmailView.as_view()),
    path('report/<int:id>/',views.ReportView.as_view()),
]