from rest_framework import routers

from tasks.views import TasksViewSet

tasks_url = routers.SimpleRouter()
tasks_url.register(r"", TasksViewSet, basename="tasks")

urlpatterns = [
]

urlpatterns += tasks_url.urls
