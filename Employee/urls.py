from django.urls import path,include
from . import views


urlpatterns = [
    path("userprofile/<slug:profile>/",views.UserProfileView.as_view()),
    path("csv/",views.CSVtoUserProfile.as_view()),


]