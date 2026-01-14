from django.urls import path, reverse_lazy
from . import views

app_name = 'movie'
urlpatterns = [
    path('', views.MovieListView.as_view(), name='movie_list'),
    path('<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('create/', views.MovieCreateView.as_view(), name='movie_create'),
    path('<int:pk>/update/', views.MovieUpdateView.as_view(), name='movie_update'),
    path('<int:pk>/delete/', views.MovieDeleteView.as_view(success_url=reverse_lazy('movie_list')), name='movie_delete'),
    path('movie/<int:pk>/favorite', views.AddFavoriteView.as_view(), name='movie_favorite'),
    path('movie/<int:pk>/unfavorite', views.DeleteFavoriteView.as_view(), name='movie_unfavorite'),
    path('movie/<int:pk>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('search/', views.MovieListView.as_view(), name='search'),
]
