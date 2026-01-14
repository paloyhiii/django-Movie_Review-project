from django.contrib import admin
from .models import Movie, Director, Actor, Genre, Review

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'director', 'actors', 'owner', 'created_at', 'updated_at')
    fields = ['title', 'release_year', 'description', 'director', 'genres', 'actors', 'picture']
    readonly_fields = ('owner',)

    def created_at(self, obj):
        return obj.created_at
    created_at.admin_order_field = 'created_at'
    created_at.short_description = 'Created At'


    def updated_at(self, obj):
        return obj.updated_at
    updated_at.admin_order_field = 'updated_at'
    updated_at.short_description = 'Updated At'

class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    readonly_fields = ('created_at',)

    def created_at(self, obj):
        return obj.created_at
    created_at.admin_order_field = 'created_at'
    created_at.short_description = 'Created At'

class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    readonly_fields = ('created_at',)

    def created_at(self, obj):
        return obj.created_at
    created_at.admin_order_field = 'created_at'
    created_at.short_description = 'Created At'

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'owner', 'rating', 'created_at')
    readonly_fields = ('owner', 'created_at', 'created_at')

    def updated_at(self, obj):
        return obj.updated_at
    updated_at.admin_order_field = 'updated_at'
    updated_at.short_description = 'Updated At'

admin.site.register(Movie, MovieAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Actor, ActorAdmin)
admin.site.register(Genre)
admin.site.register(Review, ReviewAdmin)



