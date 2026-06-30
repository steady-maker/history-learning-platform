from rest_framework import routers

from biz.views.prompt import PromptViewSet
from biz.views.question_bank import QuestionViewSet
from biz.views.tag import TagViewSet
from biz.views.web_user import WebUserViewSet, WebUserFeedbackViewSet

biz_url = routers.SimpleRouter()
biz_url.register(r'web_user', WebUserViewSet, basename='web_user')
biz_url.register(r'user_feedback', WebUserFeedbackViewSet, basename='user_feedback')
biz_url.register(r'question_bank', QuestionViewSet, basename='question_bank')
biz_url.register(r'tag', TagViewSet, basename='tag')
biz_url.register(r'prompt', PromptViewSet, basename='prompt')

urlpatterns = [
]

urlpatterns += biz_url.urls