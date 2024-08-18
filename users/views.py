from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.db.models import Q


class CreateUserView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class CustomUserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class SearchUserView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    pagination_class = CustomUserPagination
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = CustomUser.objects.all()
        search_keyword = self.request.query_params.get('search', '')

        if search_keyword:
            queryset = queryset.filter(
                Q(email__iexact=search_keyword) |
                Q(name__icontains=search_keyword)
            )

        return queryset
