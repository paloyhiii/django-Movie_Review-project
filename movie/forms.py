from django import forms
from .models import Movie, Review, Director, Actor, Genre
from django.core.files.uploadedfile import InMemoryUploadedFile
from movie.humanize import naturalsize
from taggit.forms import TagField

class MovieForm(forms.ModelForm):
    max_upload_limit = 5 * 1024 * 1024  # Limit file size to 5MB
    max_upload_limit_text = naturalsize(max_upload_limit)

    picture = forms.FileField(required=False,
              label='Upload Poster (<= ' + max_upload_limit_text + ')')
    upload_field_name = 'picture'

    director_name = forms.CharField(label="Director Name")
    actors = forms.CharField(required=False,
             help_text='Separate names with commas')

    genres = TagField(required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Add genres (comma separated)',
            'class': 'form-control genre-input',
            'style': 'background-color: var(--card-bg);' +
                     'color: rgba(255, 255, 255, 0.6);' +
                     'border: 1px solid rgba(255,255,255,0.1);',
        })
    )
    class Meta:
        model = Movie
        fields = ['title', 'release_year', 'description', 'director_name',
                    'genres', 'actors', 'picture']
        labels = {
            'genres': 'Genres',
        }


    def save(self, commit=True):
        instance = super(MovieForm, self).save(commit=False)

        f = instance.picture
        if isinstance(f, InMemoryUploadedFile):  # If it is an uploaded file
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr  # Save the movie poster file

        # Handle director - create or get the director object
        name = self.cleaned_data.get('director_name')
        director, _ = Director.objects.get_or_create(name=name)
        instance.director = director

        if commit:
            instance.save()

        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['director_name'].initial = self.instance.director.name if self.instance.director else ''
            tag_names = ', '.join(tag.name for tag in self.instance.genres.all())
            self.initial['genres'] = tag_names





class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'cols': 50,
                'placeholder': 'Write your review here...'
            }),
            'rating': forms.RadioSelect(choices=[(i, f"{i} Stars") for i in range(1, 6)])
        }


    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not (1 <= rating <= 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ['name', 'biography']

class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ['name', 'biography']

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']

class MovieSearchForm(forms.Form):
    search_query = forms.CharField(max_length=100, required=False, label="Search Movies")



