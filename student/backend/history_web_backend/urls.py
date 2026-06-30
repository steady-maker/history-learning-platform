"""
URL configuration for history_web_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


from history_web_backend import settings
from system.views.file import FileViewSet
from system.views.login import LoginView, CaptchaView, RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', LoginView.as_view()),
    path('api/register/', RegisterView.as_view()),
    path('api/file/', FileViewSet.as_view({'get': 'download', 'post': 'upload'})),
    path('api/captcha/', CaptchaView.as_view()),
    path('api/system/', include('system.urls')),
    path('api/question/',include('question.urls')),
    path('api/user/',include('web_user.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
