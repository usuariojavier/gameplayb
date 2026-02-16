"""
Seed script to populate the database with sample data for testing.
Run with: python3.11 manage.py shell < seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gameplay.settings')
django.setup()

from clips.models import User, Game, Clip, Rating, Comment
from django.utils import timezone
from datetime import timedelta
import random

# Create users
users = []
user_data = [
    ("ProGamer99", "pro@example.com", "Competitive FPS player"),
    ("NinjaClips", "ninja@example.com", "Highlight reel specialist"),
    ("PixelQueen", "pixel@example.com", "Retro gaming enthusiast"),
    ("ShadowStrike", "shadow@example.com", "Stealth gameplay master"),
    ("RocketLeaguer", "rocket@example.com", "Aerial goals only"),
]

for username, email, bio in user_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "bio": bio}
    )
    if created:
        user.set_password("test1234")
        user.save()
    users.append(user)

print(f"Created {len(users)} users")

# Create games
games_data = [
    ("Counter-Strike 2", "https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg", "Tactical FPS"),
    ("Valorant", "https://cdn1.epicgames.com/offer/cbd5b3d310a54b12bf3fe8c41994174f/EGS_VALORANT_RiotGames_S1_2560x1440-b88adde6a9e24d0192ccbe8b5c07ec45", "Tactical shooter by Riot Games"),
    ("Rocket League", "https://cdn.akamai.steamstatic.com/steam/apps/252950/header.jpg", "Soccer with rocket-powered cars"),
    ("League of Legends", "https://cdn1.epicgames.com/offer/24b9b5e323bc40eea252a10cdd3b2f10/EGS_LeagueofLegends_RiotGames_S1_2560x1440-80471666c140f790f28dff68d72c384b", "MOBA by Riot Games"),
    ("Fortnite", "https://cdn1.epicgames.com/offer/fn/23BR_C5S1_EGS_Launcher_Blade_2560x1440_2560x1440-50f77e8b8e42d2e5e6e8e8e8e8e8e8e8", "Battle Royale"),
    ("Minecraft", "https://cdn.akamai.steamstatic.com/steam/apps/1672970/header.jpg", "Sandbox survival game"),
    ("Apex Legends", "https://cdn.akamai.steamstatic.com/steam/apps/1172470/header.jpg", "Battle Royale FPS"),
    ("Overwatch 2", "https://cdn.akamai.steamstatic.com/steam/apps/2357570/header.jpg", "Team-based hero shooter"),
    ("Call of Duty: Warzone", "https://cdn.akamai.steamstatic.com/steam/apps/1702930/header.jpg", "Battle Royale FPS"),
    ("grand theft auto v", "https://cdn.akamai.steamstatic.com/steam/apps/271590/header.jpg", "Open world action-adventure"),
]

games = []
for name, cover, desc in games_data:
    game, _ = Game.objects.get_or_create(
        name=name,
        defaults={"cover_url": cover, "description": desc}
    )
    games.append(game)

print(f"Created {len(games)} games")

# Create clips with real YouTube IDs of gaming clips
clips_data = [
    ("Insane AWP Ace on Mirage", "dQw4w9WgXcQ", 0, 0, "Clean 5k with the AWP"),
    ("1v5 Clutch Retake", "jNQXAC9IVRw", 1, 0, "Never give up on the retake"),
    ("Phantom 4K Eco Round", "9bZkp7q19f0", 0, 1, "Eco round destruction"),
    ("Ceiling Shot Double Tap", "kJQP7kiw5Fk", 2, 2, "Mechanical ceiling shot goal"),
    ("Air Dribble to Musty Flick", "RgKAFK5djSk", 3, 2, "Smooth air dribble combo"),
    ("Pentakill with Yasuo", "hT_nvWreIhg", 4, 3, "Yasuo outplay in teamfight"),
    ("Baron Steal with Smite", "JGwWNGJdvx8", 1, 3, "Perfectly timed baron steal"),
    ("90s Build Battle Win", "fJ9rUzIMcZQ", 0, 4, "Insane building mechanics"),
    ("Redstone Calculator", "2Vv-BfVoq4g", 3, 5, "Working calculator in Minecraft"),
    ("Kraber 360 No-Scope", "CevxZvSJLk8", 2, 6, "Kraber highlight reel"),
    ("Team Wipe with Genji Blade", "dQw4w9WgXcQ", 4, 7, "Dragonblade team wipe"),
    ("Deagle Ace Pistol Round", "jNQXAC9IVRw", 1, 0, "Desert Eagle ace"),
]

clips = []
for i, (title, yt_id, user_idx, game_idx, desc) in enumerate(clips_data):
    clip, created = Clip.objects.get_or_create(
        title=title,
        defaults={
            "youtube_id": yt_id,
            "author": users[user_idx],
            "game": games[game_idx],
            "description": desc,
        }
    )
    if created:
        # Stagger creation dates within last 7 days for weekly top
        clip.created_at = timezone.now() - timedelta(days=random.randint(0, 6), hours=random.randint(0, 23))
        clip.save()
    clips.append(clip)

print(f"Created {len(clips)} clips")

# Create ratings
rating_count = 0
for clip in clips:
    raters = [u for u in users if u != clip.author]
    num_ratings = random.randint(2, len(raters))
    for user in random.sample(raters, num_ratings):
        _, created = Rating.objects.get_or_create(
            user=user,
            clip=clip,
            defaults={"value": random.randint(2, 5)}
        )
        if created:
            rating_count += 1

print(f"Created {rating_count} ratings")

# Create comments
comments_data = [
    "Insane play! GG",
    "How did you hit that?!",
    "Clean mechanics",
    "This deserves more votes",
    "Tutorial when?",
    "Absolutely nutty",
    "I've watched this 10 times already",
    "What rank are you?",
]

comment_count = 0
for clip in clips[:8]:
    num_comments = random.randint(1, 4)
    commenters = random.sample(users, min(num_comments, len(users)))
    for user in commenters:
        Comment.objects.get_or_create(
            user=user,
            clip=clip,
            text=random.choice(comments_data),
        )
        comment_count += 1

print(f"Created {comment_count} comments")
print("Seed data complete!")
