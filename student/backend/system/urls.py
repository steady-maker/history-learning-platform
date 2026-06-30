from django.urls import path, re_path
from rest_framework import routers
from system.views import dictionary, user, config

system_url = routers.SimpleRouter()

urlpatterns = [
    path(r"user/user_info/", user.UserInfo.as_view()),
    re_path(r"dict_data/type/(?P<dict_type>[^/.]+)/", dictionary.DictDataViewSet.as_view()),
    re_path(r"config/key/(?P<config_key>[^/]+)", config.ConfigViewSet.as_view()),
]

urlpatterns += system_url.urls