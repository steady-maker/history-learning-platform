from rest_framework import routers

from question.views.prompt import PromptViewSet
from question.views.question_bank import QuestionViewSet
from question.views.tag import TagViewSet

url = routers.SimpleRouter()
url.register(r'question_bank', QuestionViewSet, basename='question_bank')
url.register(r'tag', TagViewSet, basename='tag')
url.register(r'prompt', PromptViewSet, basename='prompt')

urlpatterns = [
]

urlpatterns += url.urls