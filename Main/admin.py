from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(FeedbackForm)
admin.site.register(Feedback)
admin.site.register(UserProfile)
admin.site.register(UserRelation)
