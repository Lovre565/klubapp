from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import Match, Appearance

class MatchListView(ListView):
    model = Match
    ordering = ["-date"]
    template_name = "matches/match_list.html"
    context_object_name = "matches"

class MatchCreateView(CreateView):
    model = Match
    fields = ["date", "competition", "opponent", "home_away", "result"]
    template_name = "matches/match_form.html"
    success_url = reverse_lazy("matches:list")

class AppearanceCreateView(CreateView):
    model = Appearance
    fields = ["player", "minutes", "goals", "yellow", "red"]
    template_name = "matches/appearance_form.html"

    def form_valid(self, form):
        form.instance.match_id = self.kwargs["pk"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("matches:list")
