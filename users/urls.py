from django.urls import path
from .views import SearchUserView, SendFriendRequestView, AcceptFriendRequestView, RejectFriendRequestView
from .views import CreateUserView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('search/', SearchUserView.as_view(), name='user-search'),
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/accept/<int:pk>/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friend-request/reject/<int:pk>/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
]