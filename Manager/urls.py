from django.urls import path,include
from . import views


urlpatterns = [
    path('feedbackform/',views.FeedbackFormView.as_view()),
    path('t/',views.test.as_view()),
    path('feedbackform/<int:form_id>/clone/',views.CloneFeedbackFormView.as_view()),
    path('feedback/<int:form_id>/all',views.FeedbackView.as_view()),
    path('feedback/<int:feedback_id>/<slug:type>/',views.EditFeedbackView.as_view()),
    path('nominations/<int:feedback_id>/',views.NominationsView.as_view()),
    path('r-email/<int:id>/',views.RemainderEmailView.as_view()),
    path('report/<int:id>/',views.ReportView.as_view()),
    path('generatecsv/',views.GenerateCSVView.as_view()),
    path('managerfeedbacks/<slug:name>/',views.ManagerView.as_view()),
    # path('chartreport/',views.ChartReviewView.as_view()),
]
