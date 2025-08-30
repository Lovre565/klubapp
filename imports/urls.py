from django.urls import path
from . import views

app_name = "imports"

urlpatterns = [
    path("players/", views.player_import_upload, name="players_upload"),
    path("players/commit/", views.player_import_commit, name="players_commit"),
]
