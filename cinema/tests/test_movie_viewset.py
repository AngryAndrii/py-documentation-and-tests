from django.contrib.auth import get_user_model
from django.template.defaultfilters import title
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from cinema.models import Movie, Genre, Actor
from cinema.serializers import MovieSerializer, MovieListSerializer

MOVIES_URL = reverse("cinema:movie-list")

def sample_movie(**params):
    defaults = {
        "title": "Sample movie",
        "description": "Sample description",
        "duration": 90,
    }
    defaults.update(params)

    return Movie.objects.create(**defaults)


class UnauthenticatedMovieViewsUsers(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(MOVIES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMovieViewsUsers(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@mail.test",
            password = "testpass12345"
        )
        self.client.force_authenticate(self.user)


    def test_movies_list(self):
        sample_movie()
        movie_with_genres = sample_movie()

        genre_1 = Genre.objects.create(name="drama")
        genre_2 = Genre.objects.create(name="horror")

        movie_with_genres.genres.add(genre_1, genre_2)

        res = self.client.get(MOVIES_URL)

        movies = Movie.objects.all()
        serializer = MovieListSerializer(movies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_filter_movies_with_genre(self):
        movie_without_genre = sample_movie()
        movie_with_genre_1 = sample_movie(title="Test movie 1")
        movie_with_genre_2 = sample_movie(title="Test movie 2")
        genre_1 = Genre.objects.create(name="Comedy")
        genre_2 = Genre.objects.create(name="Thriller")
        movie_with_genre_1.genres.add(genre_1)
        movie_with_genre_2.genres.add(genre_2)

        res = self.client.get(MOVIES_URL, {"genres": f"{genre_1.id},{genre_2.id}"})

        serializer_without_genre = MovieListSerializer(movie_without_genre)
        serializer_with_genre_1 = MovieListSerializer(movie_with_genre_1)
        serializer_with_genre_2 = MovieListSerializer(movie_with_genre_2)

        self.assertIn(serializer_with_genre_1.data, res.data)
        self.assertIn(serializer_with_genre_2.data, res.data)
        self.assertNotIn(serializer_without_genre, res.data)

    def test_filter_movies_with_actors(self):
        movie_without_actor = sample_movie()
        movie_with_actor_1 = sample_movie(title="Test movie 1")
        movie_with_actor_2 = sample_movie(title="Test movie 2")
        actor_1 = Actor.objects.create(first_name="first", last_name="first")
        actor_2 = Actor.objects.create(first_name="second", last_name="second")
        movie_with_actor_1.actors.add(actor_1)
        movie_with_actor_2.actors.add(actor_2)

        res = self.client.get(MOVIES_URL, {"actors": f"{actor_1.id},{actor_2.id}"})

        serializer_without_actor = MovieListSerializer(movie_without_actor)
        serializer_with_actor_1 = MovieListSerializer(movie_with_actor_1)
        serializer_with_actor_2 = MovieListSerializer(movie_with_actor_2)

        self.assertIn(serializer_with_actor_1.data, res.data)
        self.assertIn(serializer_with_actor_2.data, res.data)
        self.assertNotIn(serializer_without_actor, res.data)
