from django.shortcuts import render, get_object_or_404, redirect
from .models import Pokemon
from .interface import noms, preparer_stats, NB_POKEMON


def accueil(request):
    pokemons = Pokemon.objects.all().order_by("numero")
    return render(request, "pokemon/accueil.html", {"pokemons": pokemons})


def aller(request):
    numero = request.GET.get("numero")
    if numero and numero.isdigit():
        num = max(1, min(NB_POKEMON, int(numero)))
        return redirect("fiche", numero=num)
    return redirect("accueil")


def fiche(request, numero):
    pokemon = get_object_or_404(Pokemon, numero=numero)
    stats = preparer_stats(pokemon.stats)
    pokemons_liste = Pokemon.objects.values("numero", "nom").order_by("numero")

    contexte = {
        "pokemon": pokemon,
        "types": noms(pokemon.types, "type"),
        "capacites": noms(pokemon.capacites, "ability"),
        "taille_m": pokemon.taille / 10,
        "poids_kg": pokemon.poids / 10,
        "stats": stats,
        "total": sum(s["valeur"] for s in stats),
        "precedent": numero - 1 if numero > 1 else None,
        "suivant": numero + 1 if numero < NB_POKEMON else None,
        "pokemons_liste": pokemons_liste,
    }
    return render(request, "pokemon/fiche.html", contexte)