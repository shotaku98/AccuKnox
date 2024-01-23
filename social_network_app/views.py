# views.py
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from social_network_app.models import CustomUser
from social_network_app.serializers import *
import jwt
from datetime import datetime, timedelta
from django_ratelimit.decorators import ratelimit


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from social_network_app.helpers import *
# from .models import FriendRequest, UserProfile
# from serializers import FriendRequestSerializer, UserProfileSerializer
from django.shortcuts import get_object_or_404

from django.db.models import Q
from django.core.paginator import Paginator




class UserRegistrationView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get("email", "").lower()
        password = request.data.get("password")

        user = CustomUser.objects.filter(email__iexact=email).first()

        if user and user.password == password:
            access_token, refresh_token = generate_jwt_token(user)

            response = Response({"message": "Login successful"})
            response.set_cookie("access_token", str(access_token), httponly=True)
            response.set_cookie("refresh_token", str(refresh_token), httponly=True)

            return response

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class UserLogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logout successful"})

        response.delete_cookie("access_token")

        response.delete_cookie("refresh_token")

        return response


class UserStatusView(APIView):
    @check_access_token
    def get(self, request):
        return Response({"status": "logged_in"}, status=status.HTTP_200_OK)



class UserSearchView(APIView):
    @check_access_token
    def get(self, request):
        search_keyword = request.query_params.get("q")

        if not search_keyword:
            return Response(
                {"error": "Search keyword is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Search by email if the keyword matches exactly
        exact_email_user = CustomUser.objects.filter(
            email__iexact=search_keyword
        ).first()

        if exact_email_user:
            serializer = CustomUserSerializer(exact_email_user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Search by name if the keyword is a part of the name
        name_users = CustomUser.objects.filter(Q(name__icontains=search_keyword))
        limit = request.query_params.get("limit", 1)
        paginator = Paginator(name_users, limit)  # Paginate up to 10 records per page
        page_number = request.query_params.get("page", 1)
        page_users = paginator.get_page(page_number)

        serializer = CustomUserSerializer(page_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FriendRequestView(APIView):
    @check_access_token
    # @ratelimit(key='ip', rate='3/m', block=True)
    def post(self, request):
        access_token = self.request.COOKIES.get("refresh_token")
        decoded_token = jwt.decode(access_token, "SECRET", algorithms=["HS256"])
        user_profile = get_object_or_404(CustomUser, id=decoded_token["id"])
        from_user = user_profile
        to_user = get_object_or_404(CustomUser, id=request.data["to_user_id"])

        if from_user == to_user:
            return Response(
                {"error": "You cannot send a friend request to yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_request = FriendRequest.objects.filter(
            from_user=from_user, to_user=to_user, is_accepted=False
        )
        if existing_request.exists():
            return Response(
                {"error": "Friend request already sent"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()

        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @check_access_token
    def get(self, request):
        access_token = self.request.COOKIES.get("refresh_token")
        decoded_token = jwt.decode(access_token, "SECRET", algorithms=["HS256"])
        user_profile = get_object_or_404(CustomUser, id=decoded_token["id"])
        friend_requests = FriendRequest.objects.filter(
            to_user=user_profile.id, is_accepted=False
        )
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @check_access_token
    def patch(self, request):
        access_token = self.request.COOKIES.get("refresh_token")
        decoded_token = jwt.decode(access_token, "SECRET", algorithms=["HS256"])
        user_profile = get_object_or_404(CustomUser, id=decoded_token["id"])
        friend_request_id = request.query_params.get("id")
        friend_request = get_object_or_404(
            FriendRequest,
            id=friend_request_id,
            to_user=user_profile,
        )  # is_accepted=False)
        friend_request.is_accepted = True
        friend_request.save()

        # Add users to each other's friends list
        # friend_request.from_user.profile.friends.add(request.user)
        user_profile.friends.add(friend_request.from_user.id)
        user_profile_friend = get_object_or_404(
            CustomUser, id=friend_request.to_user.id
        )
        user_profile_friend.friends.add(friend_request.to_user.id)
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @check_access_token
    def delete(self, request):
        access_token = self.request.COOKIES.get("refresh_token")
        decoded_token = jwt.decode(access_token, "SECRET", algorithms=["HS256"])
        user_profile = get_object_or_404(CustomUser, id=decoded_token["id"])
        friend_request_id = request.query_params.get("id")
        friend_request = get_object_or_404(
            FriendRequest, id=friend_request_id, to_user=user_profile, is_accepted=False
        )
        friend_request.delete()
        return Response(
            {"message": "Friend request deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class FriendsListView(APIView):
    @check_access_token
    def get(self, request):
        access_token = self.request.COOKIES.get("refresh_token")

        decoded_token = jwt.decode(access_token, "SECRET", algorithms=["HS256"])

        user_profile = get_object_or_404(CustomUser, id=decoded_token["id"])
        friends = user_profile.friends.all()
        print("FRIED", friends)
        serializer = CustomUserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
