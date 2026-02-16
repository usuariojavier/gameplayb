from django.urls import path
from . import views

urlpatterns = [
    # Page routes
    path("", views.index, name="index"),
    path("games", views.games_page, name="games"),
    path("game/<slug:slug>", views.game_page, name="game"),
    path("clip/<int:clip_id>", views.clip_page, name="clip_page"),
    path("profile/<str:username>", views.profile_page, name="profile"),
    path("top-creators", views.top_creators_page, name="top_creators"),
    path("submit", views.submit, name="submit"),
    path("favorites", views.favorites_page, name="favorites"),
    path("bookmarked-creators", views.bookmarked_creators_page, name="bookmarked_creators"),
    path("edit-profile", views.edit_profile_page, name="edit_profile"),

    # Auth routes
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),

    # API routes
    path("api/clips", views.api_clips, name="api_clips"),
    
    path("api/clips/weekly-top", views.api_weekly_top, name="api_weekly_top"),
    path("api/clips/<int:clip_id>", views.api_clip_detail, name="api_clip_detail"),
    path("api/clips/<int:clip_id>/rate", views.api_rate_clip, name="api_rate_clip"),
    path("api/clips/<int:clip_id>/comments", views.api_comments, name="api_comments"),
    path("api/clips/<int:clip_id>/comments/add", views.api_add_comment, name="api_add_comment"),
    path("api/clips/<int:clip_id>/favorite", views.api_toggle_favorite, name="api_toggle_favorite"),
    path("api/creators/<int:user_id>/bookmark", views.api_toggle_bookmark_creator, name="api_toggle_bookmark_creator"),
    path("api/profile/edit", views.api_edit_profile, name="api_edit_profile"),
]
