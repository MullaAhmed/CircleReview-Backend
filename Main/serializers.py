from rest_framework import serializers
from .models import *

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelation
        fields = '__all__'

class FeedbackFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackForm
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class FeedbackStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackStatus
        fields = '__all__'