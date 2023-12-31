from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from movie_list.views import UserViewSet, request_count, reset_request_count, MovieList, CollectionsViewSet

router = SimpleRouter()
router.register('user', UserViewSet, basename='User')
router.register('all', MovieList, basename='all')
router.register('collection', CollectionsViewSet, basename='collection')

url = [
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-count/', request_count, name='request_count'),
    path('request-count/reset/', reset_request_count, name='reset_request_count'),

]

urlpatterns = router.urls + url
