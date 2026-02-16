from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models import Avg, Count
from datetime import timedelta
from django.utils import timezone


class User(AbstractUser):
    """Extended user model with gaming profile fields."""
    bio = models.TextField(max_length=300, blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")
    favorite_clips = models.ManyToManyField(
        'Clip', blank=True, related_name='favorited_by'
    )
    bookmarked_creators = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='bookmarked_by'
    )

    def __str__(self):
        return self.username

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "clips_count": self.clips.count(),
            "date_joined": self.date_joined.strftime("%b %d, %Y"),
        }


class Game(models.Model):
    """Video game entity — the central organizing axis of the platform."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    cover_url = models.URLField(blank=True, default="")
    description = models.TextField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "cover_url": self.cover_url,
            "description": self.description,
            "clips_count": self.clips.count(),
        }


class Clip(models.Model):
    """
    The primary content entity of the platform.
    Stores a cloudinary video reference and metadata. 
    """

    title = models.CharField(max_length=120)
    # resource_type='video' is vital for accepting mp4/mov and not just photos.
    video_file = CloudinaryField(resource_type='video', folder='gameplay_clips')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='clips'
    )
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='clips'
    )
    description = models.TextField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    @property
    def avg_rating(self):
        """Calculate the average star rating for this clip."""
        result = self.ratings.aggregate(avg=Avg('value'))
        return round(result['avg'], 1) if result['avg'] else 0

    @property
    def rating_count(self):
        """Count total ratings for this clip."""
        return self.ratings.count()

    def serialize(self, user=None):
        data = {
            "id": self.id,
            "title": self.title,
            # --- CORRECCIÓN CRÍTICA AQUÍ ---
            # Antes ponía youtube_id, ahora enviamos la URL de Cloudinary
            "video_url": self.video_file.url if self.video_file else "",
            # -------------------------------
            "author": self.author.username,
            "author_id": self.author.id,
            "author_avatar": self.author.avatar_url,
            "game": self.game.name,
            "game_slug": self.game.slug,
            "description": self.description,
            "avg_rating": self.avg_rating,
            "rating_count": self.rating_count,
            "created_at": self.created_at.strftime("%b %d, %Y %H:%M"),
            "comments_count": self.comments.count(),
        }
        if user and user.is_authenticated:
            data["user_rating"] = self.get_user_rating(user)
            data["is_favorited"] = user.favorite_clips.filter(id=self.id).exists()
        return data

    def get_user_rating(self, user):
        """Get the rating value a specific user gave to this clip."""
        try:
            return self.ratings.get(user=user).value
        except Rating.DoesNotExist:
            return 0

    @staticmethod
    def weekly_top(limit=10, min_votes=2):
        """
        Ranking algorithm: returns the top clips from the last 7 days.
        """
        one_week_ago = timezone.now() - timedelta(days=7)
        return (
            Clip.objects.filter(created_at__gte=one_week_ago)
            .annotate(
                avg=Avg('ratings__value'),
                votes=Count('ratings')
            )
            .filter(votes__gte=min_votes)
            .order_by('-avg', '-votes')[:limit]
        )


class Rating(models.Model):
    """
    Star rating (1-5) for a clip. Enforces one rating per user per clip.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ratings'
    )
    clip = models.ForeignKey(
        Clip, on_delete=models.CASCADE, related_name='ratings'
    )
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'clip')

    def __str__(self):
        return f"{self.user.username} -> {self.clip.title}: {self.value}★"


class Comment(models.Model):
    """
    Comments on clips.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    clip = models.ForeignKey(
        Clip, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} on {self.clip.title}"

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "user_id": self.user.id,
            "user_avatar": self.user.avatar_url,
            "text": self.text,
            "created_at": self.created_at.strftime("%b %d, %Y %H:%M"),
        }