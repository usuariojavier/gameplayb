from django.contrib import admin
from .models import User, Game, Clip, Rating, Comment


class ClipInline(admin.TabularInline):
    model = Clip
    extra = 0
    fields = ('title', 'video_file', 'author', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined')
    search_fields = ('username', 'email')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')           
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    inlines = [ClipInline]


@admin.register(Clip)
class ClipAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'game', 'video_file', 'created_at')
    list_filter = ('game', 'created_at')
    search_fields = ('title', 'author__username', 'game__name')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'clip', 'value', 'created_at')
    list_filter = ('value',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'clip', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text')
