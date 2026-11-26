from django.shortcuts import render, get_object_or_404
from .models import Pokemon
from .interface import noms, preparer_stats

# Create your views here.

def accueil(request):
    return render(request, 'pokemon/accueil.html')

def fiche(request, numero):
    pokemon = get_object_or_404(Pokemon, numero=numero)
    stats = preparer_stats(pokemon.stats)
    contexte = {
        "pokemon": pokemon,
        "types": noms(pokemon.types, "type"),
        "capacites": noms(pokemon.capacites, "ability"),
        "taille_m": pokemon.taille / 10,
        "poids_kg": pokemon.poids / 10,
        "stats": stats,
        "total": sum(s["valeur"] for s in stats),
    }
    return render(request, "pokemon/fiche.html", contexte)