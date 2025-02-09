from django.shortcuts import render
from django.views import View


class GlobalLeaderboardView(View):
    """
    View to render the global leaderboard page.
    """

    def get(self, request):
        return render(request, "leaderboard/global_leaderboard.html")


class GameLeaderboardView(View):
    """
    View to render the game leaderboard page.
    """

    def get(self, request):
        return render(request, "leaderboard/game_leaderboard.html")
