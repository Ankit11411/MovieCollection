from rest_framework import serializers

from MovieCollection.base_request import CustomValidationError
from movie_list.models import AppUser


class RegUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = AppUser
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

