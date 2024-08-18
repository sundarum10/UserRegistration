from django.urls import path
from .views import SearchUserView
from .views import CreateUserView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('search/', SearchUserView.as_view(), name='user-search'),
]