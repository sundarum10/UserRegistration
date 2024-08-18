from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.pagination import PageNumberPagination
from .serializers import CustomUserSerializer, FriendRequestSerializer
from django.db.models import Q
from rest_framework import generics, status
from .models import FriendRequest, CustomUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta


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


class SendFriendRequestView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def create(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver_id')
        receiver = get_object_or_404(CustomUser, id=receiver_id)

        # Prevent sending multiple friend requests to the same user
        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            if request.user == receiver:
                return Response({'detail': 'You cannot send a friend request to yourself.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check the rate limit
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(
            sender=request.user,
            created_at__gte=one_minute_ago
        ).count()

        if recent_requests >= 3:
            return Response({'detail': 'Rate limit exceeded. You can only send 3 requests per minute.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        friend_request = FriendRequest(sender=request.user, receiver=receiver)
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        friend_request = get_object_or_404(FriendRequest, id=kwargs['pk'], receiver=request.user)

        if friend_request.status == 'pending':
            friend_request.status = 'accepted'
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)
        return Response({'detail': 'Friend request cannot be accepted.'}, status=status.HTTP_400_BAD_REQUEST)


class RejectFriendRequestView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def update(self, request, *args, **kwargs):
        friend_request = get_object_or_404(FriendRequest, id=kwargs['pk'], receiver=request.user)

        if friend_request.status == 'pending':
            friend_request.status = 'rejected'
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)
        return Response({'detail': 'Friend request cannot be rejected.'}, status=status.HTTP_400_BAD_REQUEST)


class ListFriendsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        status = self.request.query_params.get('status')

        if status not in ['pending', 'accepted', 'rejected']:
            return FriendRequest.objects.none()  # Return an empty queryset if the status is invalid

        return FriendRequest.objects.filter(
            receiver=self.request.user,
            status=status
        )