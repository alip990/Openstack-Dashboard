from contextlib import nullcontext
from urllib import response
from rest_framework.views import APIView
from users.models import User
from rest_framework.exceptions import AuthenticationFailed
from users.serializer import UserSerializer, LoginSerializer
# Create your views here.
from rest_framework.response import Response
import jwt
from dashboard.settings import SECRET_KEY
import datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializer import UserSerializer, ChangePasswordSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        data = LoginSerializer(data=request.data)
        if data.is_valid():
            email = data.validated_data['email']
            password = data.validated_data['password']
            user = User.objects.filter(email=email).first()
            if user is None:
                raise AuthenticationFailed('User not found!')

            if not user.check_password(password):
                raise AuthenticationFailed('Incorrect Password !')

            payload = {
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=60)
            }

            token = jwt.encode(payload, SECRET_KEY,)

            response = Response()

            response.set_cookie(key='Authorization', value=token,
                                httponly=True, expires=None)

            response.data = {
                "token": token,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "has_access": True if user.openstack_username else False
            }
            return response



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password')

            user.set_password(new_password)
            user.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
