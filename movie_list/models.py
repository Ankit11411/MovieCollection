from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from MovieCollection.base_model import AppBaseModel


class AppUser(AbstractUser):

    class Gender(models.TextChoices):
        Male = 1, 'MALE'
        Female = 2, 'FEMALE'

    phone = models.CharField(max_length=14, null=True)
    isd_code = models.CharField(max_length=4, default="+91")
    gender = models.CharField(max_length=15, choices=Gender.choices, null=True)
    join_date = models.DateField(default=timezone.now)

    @property
    def token(self):
        return RefreshToken.for_user(self)


class Genres(AppBaseModel):
    title = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.title


class Movies(AppBaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    genres = models.ManyToManyField(Genres, blank=True)
    uuid = models.CharField(max_length=200)


class Collections(AppBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movies = models.ManyToManyField(Movies)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

