from django.urls import path
from rest_framework import routers

from common.views.index import GMVAPIView

urlpatterns = [
        path('index/', GMVAPIView.as_view(), name='backend_index'),
]
