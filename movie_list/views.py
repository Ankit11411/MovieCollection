from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from MovieCollection.base_request import AuthenticatedViewSet, base_methods, CustomPageNumberPagination
from movie_list.models import AppUser
from movie_list.serializers import RegUserSerializer, LoginSerializer
from django.core.cache import cache


# Create your views here.
class UserViewSet(AuthenticatedViewSet):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    serializer_class = RegUserSerializer
    http_method_names = ['post', 'get', 'put', 'patch', 'delete'] + base_methods
    queryset = AppUser.objects.all().order_by('-join_date')
    pagination_class = CustomPageNumberPagination

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=(AllowAny,))
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = AppUser.objects.create_user(username=username, password=password)
            user.save()
            access_token = RefreshToken.for_user(user).access_token

            return JsonResponse({'access_token': str(access_token)})

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=(AllowAny,))
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(**serializer.validated_data)
            access_token = RefreshToken.for_user(user).access_token
            return JsonResponse({'access_token': str(access_token)})


class MovieList(AuthenticatedViewSet):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    serializer_class = RegUserSerializer
    http_method_names = ['post', 'get', 'put', 'patch', 'delete'] + base_methods
    queryset = AppUser.objects.all().order_by('-join_date')
    pagination_class = CustomPageNumberPagination

    @action(detail=False, methods=['post'], authentication_classes=[], permission_classes=(AllowAny,))
    def register(self, request):
        pass


def request_count(request):
    count = cache.get('request_count', 0)
    return JsonResponse({'requests': count})


def reset_request_count(request):
    cache.set('request_count', 0)
    return JsonResponse({'message': 'Request count reset successfully'})
