from django.shortcuts import render
from django.views import View


from django.shortcuts import render


def index(request):
    return render(request, "index.html")


def global_leaderboard(request):
    return render(request, "leaderboard/global_leaderboard.html")


def game_leaderboard(request):
    return render(request, "leaderboard/game_leaderboard.html")


def date_leaderboard(request):
    return render(request, "leaderboard/date_level_leaderboard.html")


def game_popularity_index(request):
    return render(request, "game_popularity_index.html")
