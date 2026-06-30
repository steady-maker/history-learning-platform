from rest_framework.response import Response
from rest_framework.views import APIView
from system.serializer.user_ser import UserInfoSerializer


class UserInfo(APIView):

    def get(self, request):
        user = request.user
        serializer = UserInfoSerializer(user)
        return Response({
            "code": 200,
            "msg": "获取成功",
            "user": serializer.data
        })