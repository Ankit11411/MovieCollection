from factory import Factory, SubFactory
from movie_list.models import Movies
from django.test import TestCase
from django.test import TestCase
from movie_list.models import Genres
import factory


class MovieFactory(Factory):
    class Meta:
        model = Movies

    title = 'Sample Movie'
    genres = 'Action'


class GenresFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genres
    title = factory.Faker('word')


class MovieModelTest(TestCase):
    def test_movie_creation(self):
        movie = MovieFactory(title='Test Movie', genres='Comedy')
        self.assertEqual(movie.title, 'Test Movie')
        self.assertEqual(movie.genres, 'Comedy')


class MoviesGenresTestCase(TestCase):
    def test_create_movie_with_genres(self):
        genre = GenresFactory()

        movie = MovieFactory()
        movie.genres.add(genre)

        movie_from_db = Movies.objects.get(pk=movie.pk)
        genres_of_movie = movie_from_db.genres.all()
        self.assertEqual(genres_of_movie.count(), 1)
        self.assertEqual(genres_of_movie[0], genre)
