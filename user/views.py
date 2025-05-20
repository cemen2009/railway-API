from django.contrib.auth import get_user_model
from rest_framework import generics

from user.serializers import UserSerializer


User = get_user_model()

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = ()
