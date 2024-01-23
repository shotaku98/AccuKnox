# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("api/register/", UserRegistrationView.as_view(), name="user-registration"),
    path("api/login/", UserLoginView.as_view(), name="user-login"),
    path("api/logout/", UserLogoutView.as_view(), name="user-logout"),  # Add this line
    path("api/status/", UserStatusView.as_view(), name="user-status"),  # Add this line
    path("api/search/", UserSearchView.as_view(), name="user_search"),
    path("friend-requests/", FriendRequestView.as_view(), name="friend-requests"),
    path("friends/", FriendsListView.as_view(), name="friends-list"),
    # Add other URLs as needed
]
