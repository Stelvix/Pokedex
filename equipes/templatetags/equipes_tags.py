from django import template

from equipes.models import TAILLE_MAX_EQUIPE
from equipes.Repository.equipeRepository import EquipeRepository

register = template.Library()


@register.inclusion_tag("equipes/_ajout_depuis_fiche.html", takes_context=True)
def ajout_equipe(context, pokemon):
    """Encadré « Équipes » de la fiche d'un Pokémon.
    Utilisation dans un template : {% load equipes_tags %} puis {% ajout_equipe pokemon %}
    (comme ça, la vue de la fiche n'a pas besoin d'être modifiée)."""
    choix = []
    dans_equipes = []
    for equipe in EquipeRepository.get_all():
        membres = equipe.pokemons.all()
        if pokemon in membres:
            dans_equipes.append(equipe)
            raison = "déjà dedans"
        elif len(membres) >= TAILLE_MAX_EQUIPE:
            raison = "complète"
        else:
            raison = ""
        choix.append({"equipe": equipe, "nb": len(membres), "raison": raison})

    return {
        "pokemon": pokemon,
        "choix": choix,
        "dans_equipes": dans_equipes,
        "taille_max": TAILLE_MAX_EQUIPE,
        # nécessaires au formulaire et aux messages dans le petit template
        "csrf_token": context.get("csrf_token"),
        "messages": context.get("messages"),
    }
