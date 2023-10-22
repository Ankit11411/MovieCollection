from django.db.models import Count
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from MovieCollection.base_request import AuthenticatedViewSet, base_methods, CustomPageNumberPagination
from movie_list.models import AppUser, Movies, Collections, Genres
from movie_list.serializers import RegUserSerializer, LoginSerializer, MoviesSerializer, CollectionsSerializer, \
    CollectionDisplay
from django.core.cache import cache
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

timeout = 5
retries = Retry(total=20, backoff_factor=1, status_forcelist=[500, 502, 503, 504])

session = requests.Session()
adapter = HTTPAdapter(max_retries=retries)
session.mount('http://', adapter)
session.mount('https://', adapter)


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
    serializer_class = MoviesSerializer
    http_method_names = ['post', 'get', 'put', 'patch', 'delete'] + base_methods
    queryset = Movies.objects.all()
    pagination_class = CustomPageNumberPagination

    @action(detail=False, methods=['post'], url_path='movies', authentication_classes=[],
            permission_classes=(AllowAny,))
    def movies(self, request):
        page = request.query_params.get('page', 1)
        url = f"http://demo.credy.in/api/v1/maya/movies/?page={page}"

        api = session.get(url, timeout=timeout)
        api.raise_for_status()
        data = api.json()
        current_url = request.build_absolute_uri().split("?")[0]
        if data['next']:
            data['next'] = data['next'].replace(r"https://demo.onefin.in/api/v1/maya/movies/", current_url)
        if data['previous']:
            data['previous'] = data['previous'].replace(r"https://demo.onefin.in/api/v1/maya/movies/", current_url)
        return Response(data)


class CollectionsViewSet(AuthenticatedViewSet):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    serializer_class = CollectionsSerializer
    http_method_names = ['post', 'get', 'put', 'delete'] + base_methods
    queryset = Collections.objects.all()
    pagination_class = CustomPageNumberPagination

    def create(self, request, *args, **kwargs):
        print("CREATED")
        user = self.get_user()
        data = {**request.data, "user": user}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return JsonResponse({"collection_uuid": serializer.data['id']}, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        user = self.get_user()
        queryset = self.filter_queryset(self.get_queryset()).filter(user=user)

        page = self.paginate_queryset(queryset)
        top_genres = [i['title'] for i in Genres.objects.filter(movies__collections__user=user).annotate(
            genre_count=Count('movies__collections__movies__genres')).order_by(
            '-genre_count').values('title')[:3]]
        print(top_genres)
        if page is not None:
            serializer = CollectionDisplay(page, many=True)
            return self.get_paginated_response({"collections": serializer.data, "favourite_genres": top_genres,
                                                "is_success": True})

        serializer = CollectionDisplay(queryset, many=True).data
        return Response(serializer.data)


def request_count(request):
    count = cache.get('request_count', 0)
    return JsonResponse({'requests': count})


def reset_request_count(request):
    cache.set('request_count', 0)
    return JsonResponse({'message': 'Request count reset successfully'})
