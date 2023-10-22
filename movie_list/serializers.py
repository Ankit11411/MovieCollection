from rest_framework import serializers

from MovieCollection.base_request import CustomValidationError
from movie_list.models import AppUser, Movies, Collections, Genres
from drf_writable_nested import WritableNestedModelSerializer, UniqueFieldsMixin


class RegUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = AppUser
        fields = "__all__"


class GenresSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    class Meta:
        model = Genres
        exclude = ['created','modified','deleted']
        unique_fields = ['title']


class MoviesSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    genres = GenresSerializer(many=True)

    class Meta:
        model = Movies
        exclude = ['created','modified','deleted']


class CollectionsSerializer(WritableNestedModelSerializer):
    movies = MoviesSerializer(many=True)

    class Meta:
        model = Collections
        exclude = ['created','modified','deleted']

    def to_internal_value(self, data):
        for movie in data['movies']:
            genres_data = [genre.strip() for genre in movie['genres'].split(",")]
            genres_objs = [Genres.objects.get_or_create(title=genre) for genre in genres_data]
            movie['genres'] = [{"title": genre, "id": obj[0].pk} for genre, obj in zip(genres_data, genres_objs)]

            movie_obj, created = Movies.objects.get_or_create(uuid=movie['uuid'])
            movie['id'] = movie_obj.pk
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CollectionDisplay(serializers.ModelSerializer):
    title = serializers.CharField()
    description = serializers.CharField()
    uuid = serializers.CharField(source='id')

    class Meta:
        model = Collections
        fields = ['title','description','uuid']
