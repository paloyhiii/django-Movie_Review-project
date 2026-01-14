from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponse
from .models import Movie, Review, Fav
from .forms import MovieForm, ReviewForm
from django.db.models import Q, Avg


class MovieListView(ListView):
    model = Movie
    template_name = "movie/movie_list.html"
    context_object_name = "movie_list"

    def get_queryset(self):
        search_query = self.request.GET.get("search", '')
        sort_option = self.request.GET.get('sort', 'title-asc')
        filter_option = self.request.GET.get('filter', 'all')

        qs = Movie.objects.all().annotate(average_rating=Avg('movie_reviews__rating'))

        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            ).distinct()



        if filter_option == 'top_rated':
            qs = qs.filter(average_rating__gte=4)

        if sort_option == 'title-asc':
            qs = qs.order_by('title')
        elif sort_option == 'title-desc':
            qs = qs.order_by('-title')
        elif sort_option == 'year-asc':
            qs = qs.order_by('release_year','title')
        elif sort_option == 'year-desc':
            qs = qs.order_by('-release_year','title')
        elif sort_option == 'rating-asc':
            qs = qs.order_by('average_rating')
        elif sort_option == 'rating-desc':
            qs = qs.order_by('-average_rating')

        return qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add human-readable update times
        for movie in context['movie_list']:
            movie.natural_updated = naturaltime(movie.updated_at)

        # Add favorites if logged in
        favorites = list()
        if self.request.user.is_authenticated:
            rows = self.request.user.favorite_movie.values('id')
            favorites = [ row['id'] for row in rows ]

        context['favorites'] = favorites
        context['search'] = self.request.GET.get('search', '')
        context['sort'] = self.request.GET.get('sort', 'title-asc')
        context['filter'] = self.request.GET.get('filter', 'all')
        return context


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movie/movie_detail.html'
    context_object_name = 'movie'

    def get(self, request, pk):
        x = get_object_or_404(Movie, id=pk)
        reviews = Review.objects.filter(movie=x).order_by('-created_at')
        review_form = ReviewForm()
        genres = x.genres.names()
        context = {
            'movie': x,
            'reviews': reviews,
            'range' : range(1, 6),
            'review_form': review_form,
            'genres': genres,
        }
        if request.user.is_authenticated:
           context['user'] = request.user
        return render(request, self.template_name, context)



class MovieCreateView(CreateView):
    model = Movie
    form_class = MovieForm
    template_name = 'movie/movie_create.html'
    success_url = reverse_lazy('movie:movie_list')

    def get(self, request, pk=None):
        form = MovieForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = MovieForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        movie = form.save(commit=False)
        movie.owner = self.request.user
        movie.save()
        form.save_m2m()

        return redirect(self.success_url)

class MovieUpdateView(LoginRequiredMixin, UpdateView):
    model = Movie
    template_name = "movie/movie_create.html"
    form_class = MovieForm

    def get_queryset(self):
        return Movie.objects.filter(owner=self.request.user)
    def get_success_url(self):
        return reverse('movie:movie_detail', kwargs={'pk': self.object.id})
    def form_valid(self, form):
        movie = form.save(commit=False)
        movie.owner = self.request.user
        movie.save()
        form.save_m2m()
        return super().form_valid(form)


class MovieDeleteView(LoginRequiredMixin, DeleteView):
    model = Movie
    template_name = "movie/movie_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy('movie:movie_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Movie, pk=self.kwargs['pk'], owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movie'] = self.get_object()
        return context

class ReviewCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        movie = get_object_or_404(Movie, id=pk)
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.owner = request.user
            review.movie = movie
            review.save()
            messages.success(request, "Review posted successfully.")
        else:
            messages.error(request, "Error posting review: " + str(form.errors))

        return redirect(reverse('movie:movie_detail', args=[pk]))

class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "movie/review_delete.html"

    def get_success_url(self):
        movie = self.object.movie
        return reverse('movie:movie_detail', args=[movie.id])

    def get_queryset(self):
        return Review.objects.filter(owner=self.request.user)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Add PK", pk)
        movie = get_object_or_404(Movie, id=pk)
        fav = Fav(user=request.user, movie=movie)
        try:
            fav.save()
        except IntegrityError:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Delete PK", pk)
        movie = get_object_or_404(Movie, id=pk)
        try:
            Fav.objects.get(user=request.user, movie=movie).delete()
        except Fav.DoesNotExist:
            pass

        return HttpResponse()

def movie_search(request):
    search_query = request.GET.get("search", '')

    if search_query:
        query = (
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(director__name__icontains=search_query) |
            Q(actors__name__icontains=search_query)
        )

        movies = Movie.objects.filter(query).select_related('director').distinct().order_by('-created_at')[:10]
        movies = Movie.objects.filter(query).distinct().prefetch_related('genres').order_by('-created_at')
    else:
        movies = Movie.objects.all().order_by('-created_at')

    for movie in movies:
        movie.natural_updated = naturaltime(movie.updated_at)

    context = {
        'movies': movies[:10],
        'search_query': search_query,
    }

    return render(request, 'movie/movie_list.html', context)





