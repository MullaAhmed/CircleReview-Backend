from django.urls import path,include
from . import views


urlpatterns = [
    path("userprofile/<slug:company>/<int:id>/",views.UserProfileView.as_view()),
    path("team/<slug:company>/<int:id>/",views.TeamView.as_view()),
    path("csv/",views.CSVtoUserProfile.as_view()),


]