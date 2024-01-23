from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import jwt

def check_access_token(view_func):
    def _wrapped_view(self, request, *args, **kwargs):
        access_token = self.request.COOKIES.get("refresh_token")

        if not access_token:
            # Access token is not present, return 403
            return JsonResponse(
                {"error": "Access token is missing"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            decoded_token = jwt.decode(access_token, "SECRET", algorithms=["HS256"])
            # Check if the token has expired
            expiration_time = datetime.utcfromtimestamp(decoded_token["exp"])
            if expiration_time < datetime.utcnow():
                return JsonResponse(
                    {"error": "Access token has expired"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"error": "Access token has expired"}, status=status.HTTP_403_FORBIDDEN
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {"error": "Invalid access token"}, status=status.HTTP_403_FORBIDDEN
            )

        # Call the original view function if everything is valid
        return view_func(self, request, *args, **kwargs)

    return _wrapped_view


def generate_jwt_token(user_object, secret_key="SECRET"):
    access_exp_time = datetime.utcnow() + timedelta(minutes=15)

    refresh_exp_time = datetime.utcnow() + timedelta(days=365)

    access_payload = {
        "id": str(user_object.id),
        "email": user_object.email,
        "exp": access_exp_time,
    }

    refresh_payload = {
        "id": str(user_object.id),
        "email": user_object.email,
        "exp": refresh_exp_time,
    }

    access_token = jwt.encode(access_payload, secret_key, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, secret_key, algorithm="HS256")

    return access_token, refresh_token

