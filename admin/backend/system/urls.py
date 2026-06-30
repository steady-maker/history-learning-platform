from django.urls import path
from rest_framework import routers

from system.views import menu, dictionary, user, role, config, login_log
from system.views.user import UserViewSet

system_url = routers.SimpleRouter()
system_url.register(r"user", user.UserViewSet, basename="user")
system_url.register(r"menu", menu.MenuViewSet, basename="menu")
system_url.register(r"role", role.RoleViewSet, basename="role")
system_url.register(r"config", config.ConfigViewSet, basename="config")
system_url.register(r"dict_type", dictionary.DictTypeViewSet, basename="dict_type")
system_url.register(r"dict_data", dictionary.DictDataViewSet, basename="dict_data")
system_url.register(r"login_log", login_log.LoginLogViewSet, basename="login_log")

urlpatterns = [
]

urlpatterns += system_url.urls