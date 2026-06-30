from django.urls import path
from rest_framework import routers

import web_user
from web_user.views.user_info import WebUserViewSet, UserFeedbackViewSet

url = routers.SimpleRouter()
url.register(r'web_user', WebUserViewSet, basename='web_user')


urlpatterns = [
    path(r"web_user/user_feedback/", UserFeedbackViewSet.as_view()),
]

urlpatterns += url.urls