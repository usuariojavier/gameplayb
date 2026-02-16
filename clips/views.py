#capstone/clips/views.py
import json
import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Avg, Count

from .models import User, Game, Clip, Rating, Comment
# PAGE VIEWS

def index(request):
    games = Game.objects.all()
    weekly_top = Clip.weekly_top(limit=10, min_votes=1)
    return render(request, "clips/index.html", {
        "games": games,
        "weekly_top": weekly_top,
    })


def game_page(request, slug):
    game = get_object_or_404(Game, slug=slug)
    games = Game.objects.all()
    return render(request, "clips/game.html", {
        "game": game,
        "games": games,
    })


def clip_page(request, clip_id):
    clip = get_object_or_404(Clip, id=clip_id)
    games = Game.objects.all()
    return render(request, "clips/clip.html", {
        "clip": clip,
        "games": games,
    })


def profile_page(request, username):
    profile_user = get_object_or_404(User, username=username)
    games = Game.objects.all()
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = request.user.bookmarked_creators.filter(
            id=profile_user.id
        ).exists()
    return render(request, "clips/profile.html", {
        "profile_user": profile_user,
        "games": games,
        "is_bookmarked": is_bookmarked,
    })


def games_page(request):
    games = Game.objects.annotate(num_clips=Count('clips')).order_by('-num_clips')
    return render(request, "clips/games.html", {
        "games": games,
    })


def top_creators_page(request):
    creators = (
        User.objects.annotate(
            avg_rating=Avg('clips__ratings__value'),
            total_clips=Count('clips'),
            total_ratings=Count('clips__ratings')
        )
        .filter(total_clips__gte=1, total_ratings__gte=1)
        .order_by('-avg_rating', '-total_clips')[:20]
    )
    games = Game.objects.all()
    return render(request, "clips/top_creators.html", {
        "creators": creators,
        "games": games,
    })


@login_required
def submit(request):  # Renómbrar a 'submit' si urls.py la llama así,
    # 1. Si el usuario envía el formulario (POST)
    if request.method == "POST":
        # Recogemos los datos del HTML
        title = request.POST.get("title")
        description = request.POST.get("description")
        game_id = request.POST.get("game")
        
        #  Aquí viene el archivo de video gracias a enctype="multipart/form-data"
        video_file = request.FILES.get("video_file")

        # Validación básica
        if not title or not game_id or not video_file:
            return render(request, "clips/submit.html", {
                "games": Game.objects.all(),
                "error": "Por favor, completa todos los campos obligatorios."
            })

        # Buscamos el juego
        game = get_object_or_404(Game, id=game_id)

        # 2. CREAMOS EL CLIP
        # Django + Cloudinary hacen la magia aquí automáticamente  youtube_id
        # Al pasar 'video_file' al campo del modelo, se inicia la subida a la nubeee
        clip = Clip.objects.create(
            author=request.user,
            title=title,
            description=description,
            game=game,
            video_file=video_file  # Aquí ocurre la subida!
        )

        # 3. Éxito: Redirigimos al usuario a ver su nuevo clip
        return redirect("clip_page", clip_id=clip.id)

    # ---------------------------------------------------------
    # 4. Si el usuario solo está visitando la página (GET)
    games = Game.objects.all()
    return render(request, "clips/submit.html", {
        "games": games,
    })


@login_required
def favorites_page(request):
    games = Game.objects.all()
    return render(request, "clips/favorites.html", {
        "games": games,
    })


@login_required
def bookmarked_creators_page(request):
    games = Game.objects.all()
    creators = request.user.bookmarked_creators.all()
    return render(request, "clips/bookmarked_creators.html", {
        "games": games,
        "creators": creators,
    })


@login_required
def edit_profile_page(request):
    games = Game.objects.all()
    return render(request, "clips/edit_profile.html", {
        "games": games,
    })


# AUTH VIEWS

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "clips/login.html", {
                "message": "Invalid username and/or password.",
                "games": Game.objects.all(),
            })
    return render(request, "clips/login.html", {
        "games": Game.objects.all(),
    })


def logout_view(request):
    logout(request)
    return redirect("index")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "clips/register.html", {
                "message": "Passwords must match.",
                "games": Game.objects.all(),
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "clips/register.html", {
                "message": "Username already taken.",
                "games": Game.objects.all(),
            })
        login(request, user)
        return redirect("index")
    return render(request, "clips/register.html", {
        "games": Game.objects.all(),
    })


# API ENDPOINTS

def api_clips(request):
    game_slug = request.GET.get("game", "")
    sort = request.GET.get("sort", "recent")
    page_num = request.GET.get("page", 1)

    clips = Clip.objects.all()

    if game_slug:
        clips = clips.filter(game__slug=game_slug)

    if sort == "top":
        clips = clips.annotate(
            avg=Avg('ratings__value'),
            votes=Count('ratings')
        ).order_by('-avg', '-votes')
    else:
        clips = clips.order_by('-created_at')

    paginator = Paginator(clips, settings.CLIPS_PER_PAGE)
    page = paginator.get_page(page_num)

    return JsonResponse({
        "clips": [clip.serialize(request.user) for clip in page],
        "has_next": page.has_next(),
        "page": page.number,
        "total_pages": paginator.num_pages,
    })


def api_clip_detail(request, clip_id):
    clip = get_object_or_404(Clip, id=clip_id)
    return JsonResponse(clip.serialize(request.user))


@csrf_exempt
@login_required
def api_submit_clip(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=400)

    data = json.loads(request.body)
    title = data.get("title", "").strip()
    youtube_url = data.get("youtube_url", "").strip()
    game_id = data.get("game_id")
    description = data.get("description", "").strip()

    if not title or not youtube_url or not game_id:
        return JsonResponse({"error": "Title, YouTube URL, and game are required."}, status=400)

    youtube_id = extract_youtube_id(youtube_url)
    if not youtube_id:
        return JsonResponse({"error": "Invalid YouTube URL."}, status=400)

    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return JsonResponse({"error": "Game not found."}, status=404)

    clip = Clip.objects.create(
        title=title,
        youtube_id=youtube_id,
        author=request.user,
        game=game,
        description=description,
    )

    return JsonResponse(clip.serialize(request.user), status=201)


# ✅ ENDPOINT CORREGIDO - Votos Funcionales
@csrf_exempt
def api_rate_clip(request, clip_id):
    """
    Rate a clip with stars (1-5).
    
    Espera POST con JSON: {"value": 1-5}
    Retorna:
    {
        "success": true,
        "avg_rating": float,
        "rating_count": int,
        "user_rating": int
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=400)

    # ✅ Verificar autenticación
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Must be logged in to rate."}, status=403)

    clip = get_object_or_404(Clip, id=clip_id)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    
    value = data.get("value")

    # ✅ Validar que value existe
    if value is None:
        return JsonResponse({"error": "Value is required."}, status=400)
    
    # ✅ Convertir a int y validar
    try:
        value = int(value)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Value must be an integer."}, status=400)

    if value < 1 or value > 5:
        return JsonResponse({"error": "Rating must be 1-5."}, status=400)

    # ✅ No permitir votar tu propio clip
    if clip.author == request.user:
        return JsonResponse({"error": "Cannot rate your own clip."}, status=403)

    # ✅ Crear o actualizar el rating
    rating, created = Rating.objects.update_or_create(
        user=request.user,
        clip=clip,
        defaults={"value": value}
    )

    return JsonResponse({
        "success": True,
        "avg_rating": clip.avg_rating,
        "rating_count": clip.rating_count,
        "user_rating": value,
    }, status=200)


def api_comments(request, clip_id):
    clip = get_object_or_404(Clip, id=clip_id)
    comments = clip.comments.all()
    return JsonResponse({
        "comments": [c.serialize() for c in comments]
    })


@csrf_exempt
@login_required
def api_add_comment(request, clip_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=400)

    clip = get_object_or_404(Clip, id=clip_id)
    data = json.loads(request.body)
    text = data.get("text", "").strip()

    if not text:
        return JsonResponse({"error": "Comment text required."}, status=400)

    comment = Comment.objects.create(
        user=request.user,
        clip=clip,
        text=text,
    )

    return JsonResponse(comment.serialize(), status=201)


@csrf_exempt
@login_required
def api_toggle_favorite(request, clip_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT required."}, status=400)

    clip = get_object_or_404(Clip, id=clip_id)

    if request.user.favorite_clips.filter(id=clip.id).exists():
        request.user.favorite_clips.remove(clip)
        is_favorited = False
    else:
        request.user.favorite_clips.add(clip)
        is_favorited = True

    return JsonResponse({"is_favorited": is_favorited})


@csrf_exempt
@login_required
def api_toggle_bookmark_creator(request, user_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT required."}, status=400)

    creator = get_object_or_404(User, id=user_id)

    if creator == request.user:
        return JsonResponse({"error": "Cannot bookmark yourself."}, status=400)

    if request.user.bookmarked_creators.filter(id=creator.id).exists():
        request.user.bookmarked_creators.remove(creator)
        is_bookmarked = False
    else:
        request.user.bookmarked_creators.add(creator)
        is_bookmarked = True

    return JsonResponse({"is_bookmarked": is_bookmarked})


@csrf_exempt
@login_required
def api_edit_profile(request):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT required."}, status=400)

    data = json.loads(request.body)
    bio = data.get("bio", "").strip()
    avatar_url = data.get("avatar_url", "").strip()

    request.user.bio = bio[:300]
    request.user.avatar_url = avatar_url
    request.user.save()

    return JsonResponse(request.user.serialize())


def api_weekly_top(request):
    clips = Clip.weekly_top(limit=10, min_votes=1)
    return JsonResponse({
        "clips": [
            {
                "id": c.id,
                "title": c.title,
                "video_url": c.video_file.url if c.video_file else "",
                "author": c.author.username,
                "author_id": c.author.id,
                "game": c.game.name,
                "game_slug": c.game.slug,
                "avg_rating": round(c.avg, 1) if c.avg else 0,
                "rating_count": c.votes,
                "created_at": c.created_at.strftime("%b %d, %Y %H:%M"),
            }
            for c in clips
        ]
    })


# UTILITY

def extract_youtube_id(url):
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None