from django.urls import path
from . import views

app_name = "matches"

urlpatterns = [
    path("", views.MatchListView.as_view(), name="list"),
    path("new/", views.MatchCreateView.as_view(), name="create"),
    path("<int:pk>/appearances/new/", views.AppearanceCreateView.as_view(), name="appearance_create"),
]
