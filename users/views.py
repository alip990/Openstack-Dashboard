from contextlib import nullcontext
from urllib import response
from rest_framework.views import APIView
from users.models import User
from rest_framework.exceptions import AuthenticationFailed
from users.serializer import UserSerializer
# Create your views here.
from rest_framework.response import Response
import jwt
from dashboard.settings import SECRET_KEY
import datetime


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password !')

        payload ={
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=60)
        }
 
        token = jwt.encode(payload, 'secret', )

        response = Response()

        response.set_cookie(key='Authorization', value=token,
                            httponly=True, expires=None)

        response.data = {
            "token": token
        }
        return Response(user)
