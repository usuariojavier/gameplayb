<!-- clips/templates/clips/clip.html -->

{% extends "clips/layout.html" %}
{% load static %}
{% block title %}{{ clip.title }} — Gameplay{% endblock %}

{% block content %}
<div class="clip-detail">
    <!-- Video Embed -->
    <div class="clip-thumbnail">
        <video 
            width="100%" 
            height="450"
            controls
            autoplay
            style="background: #000; border-radius: var(--radius-lg);">
            <source src="{{ clip.video_file.url }}" type="video/mp4">
            Tu navegador no soporta HTML5 video.
        </video>
    </div>

    <!-- Clip Info -->
    <div class="clip-detail-info">
        <h1 style="font-size:1.4rem; margin-bottom:0.5rem;">{{ clip.title }}</h1>
        <div class="clip-meta" style="margin-bottom:0.75rem;">
            <a href="{% url 'profile' clip.author.username %}">{{ clip.author.username }}</a>
            <a href="{% url 'game' clip.game.slug %}" class="clip-game-tag">{{ clip.game.name }}</a>
            <span>{{ clip.created_at|date:"M d, Y" }}</span>
        </div>

        {% if clip.description %}
        <p style="color:var(--text-secondary); margin-bottom:1rem;">{{ clip.description }}</p>
        {% endif %}

        <!-- Rating -->
        <div class="rating-info" style="margin-bottom:0.75rem;">
            <div class="stars" id="clipStars" data-clip-id="{{ clip.id }}" data-user-rating="0">
                {% for i in "12345" %}
                <span class="star" data-value="{{ forloop.counter }}">&#9733;</span>
                {% endfor %}
            </div>
            <span class="rating-avg" id="clipAvg">{{ clip.avg_rating }}</span>
            <span class="rating-count" id="clipCount">({{ clip.rating_count }} votes)</span>
        </div>

        <!-- Actions -->
        <div class="clip-actions">
            {% if user.is_authenticated %}
            <button class="btn-action" id="favoriteBtn" data-clip-id="{{ clip.id }}">
                &#9829; <span id="favText">Favorite</span>
            </button>
            {% endif %}
            <button class="btn-action" onclick="navigator.clipboard.writeText(window.location.href)">
                &#128279; Share
            </button>
        </div>
    </div>

    <!-- Comments Section -->
    <div class="comments-section">
        <h3 id="commentsTitle">Comments</h3>

        {% if user.is_authenticated %}
        <div class="comment-form">
            <input type="text" id="commentInput" class="form-control" placeholder="Write a comment..." maxlength="500">
            <button id="commentBtn" class="btn btn-primary btn-sm">Post</button>
        </div>
        {% else %}
        <p style="color:var(--text-muted); margin-bottom:1rem; font-size:0.9rem;">
            <a href="{% url 'login' %}">Log in</a> to leave a comment.
        </p>
        {% endif %}

        <div id="commentsList"></div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'clips/js/clips.js' %}"></script>
<script>
    initClipDetail({{ clip.id }});
</script>
{% endblock %}