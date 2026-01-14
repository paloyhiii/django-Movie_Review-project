from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager


class Director(models.Model):
    name = models.CharField(max_length=100)
    biography = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Actor(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=256)
    release_year = models.IntegerField()
    description = models.TextField()
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True)
    actors = models.CharField(max_length=256)
    genres = TaggableManager(blank=True,verbose_name="Genres")
    picture = models.ImageField(upload_to='movie_create/', null=True, blank=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, blank=True,
        help_text='The MIMEType of the file')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='Fav', related_name='favorite_movie')
    review = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='Review', related_name='reviews_owned')

    def __str__(self):
        return self.title

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE,
            related_name='movie_reviews')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.movie.title} by {self.owner.username}"

class Fav(models.Model) :
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
            related_name ='movie_favorites')

    # https://docs.djangoproject.com/en/4.2/ref/models/options/#unique-together
    class Meta:
        unique_together = ('movie', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.movie.title[:10])



