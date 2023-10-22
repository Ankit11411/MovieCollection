from django.contrib import admin
from movie_list.models import AppUser, Genres, Movies, Collections


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Collections)
class CollectionsAdmin(admin.ModelAdmin):
    pass


@admin.register(Movies)
class MoviesAdmin(admin.ModelAdmin):
    pass


@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    pass
