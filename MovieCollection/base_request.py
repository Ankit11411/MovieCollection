from django.db import models
from django.contrib.auth.models import AnonymousUser
from rest_framework import viewsets, status, exceptions
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BaseRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import AuthenticationFailed
import json
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from django.utils.translation import gettext_lazy as _
from movie_list.models import AppUser

base_methods = ['head', 'options', 'trace']


class SuccessAPIRenderer(BaseRenderer):
    media_type = 'application/json'
    format = 'json'

    def render(self, data: dict, accepted_media_type=None, renderer_context: dict = None):
        if data is not None:
            if data.__contains__('error'):
                return json.dumps(data)
            elif data.__contains__('data'):
                return json.dumps(data)
            else:
                return json.dumps({"data": data})
        return b''


class BaseViewSet(viewsets.ModelViewSet):
    queryset = None
    serializer_class = None
    renderer_classes = (SuccessAPIRenderer, BrowsableAPIRenderer)
    permission_classes = ()

    def get_user(self) -> AppUser:
        user = self.request.user
        if isinstance(user, AnonymousUser) or user is None:
            raise AuthenticationFailed("User is not valid.")
        return user


class MultiSerializerViewSet(BaseViewSet):
    """
    Inherit this class, then define a dictionary of serializers WRT the action.
    Actions are 'list','create','retrieve','update','partial_update','destroy' for a DRF ModelViewSet
    """
    queryset = None
    serializer_class = {
        "default": None,
    }

    def get_serializer_class(self):
        return self.serializer_class.get(self.action, self.serializer_class.get("default"))


class AuthenticatedViewSet(BaseViewSet):
    """
    Inherit this ViewSet to make the API secure.
    """
    permission_classes = (IsAuthenticated,)

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if response is not None:
            response_data = {
                'data': response.data,
                'status': [response.status_code]
            }
            response.data = response_data
        return response

    def perform_destroy(self, instance):
        # instance.deleted = True
        instance.delete()
        instance.save()


class AuthenticatedViewSetWithDelete(BaseViewSet):
    """
    Inherit this ViewSet to make the API secure.
    """
    permission_classes = (IsAuthenticated,)

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if response is not None:
            response_data = {
                'data': response.data,
                'status': [response.status_code]
            }
            response.data = response_data
        return response


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'size'  # items per page
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'data': data,
        }, status=status.HTTP_200_OK)


class FilterSetMixin(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = None
    filterset_class = None


class CustomValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = detail
        # self.detail = _get_error_details(detail, code)



