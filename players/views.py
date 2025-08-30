from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import Player

class PlayerListView(ListView):
    model = Player
    template_name = "players/player_list.html"
    context_object_name = "players"
    paginate_by = 20  # možeš i maknuti

class PlayerCreateView(CreateView):
    model = Player
    fields = ["first_name", "last_name", "dob", "position"]
    template_name = "players/player_form.html"
    success_url = reverse_lazy("players:list")
