from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from equipes.forms import AjoutPokemonForm, ChoixEquipeForm, NomEquipeForm
from equipes.models import TAILLE_MAX_EQUIPE
from equipes.Repository.equipeRepository import EquipeRepository

# Fonctionnement :
# - liste et detail affichent les pages (GET) ;
# - chaque bouton envoie un formulaire (POST) vers sa propre vue
#   (creer, renommer, supprimer, ajouter, retirer), qui fait l'action,
#   ajoute un message de réussite ou d'erreur, puis redirige vers une page.


# ---------- Outils ----------

def _get_equipe_ou_404(equipe_id):
    equipe = EquipeRepository.get_by_id(equipe_id)
    if equipe is None:
        raise Http404("Cette équipe n'existe pas.")
    return equipe


def _afficher_erreurs(request, erreurs):
    """Affiche des erreurs : celles d'un formulaire ou d'une ValidationError."""
    if isinstance(erreurs, ValidationError):
        liste = erreurs.messages
    else:  # form.errors : {"champ": ["erreur", ...]}
        liste = [e for erreurs_champ in erreurs.values() for e in erreurs_champ]
    for erreur in liste:
        messages.error(request, erreur)


# ---------- Pages ----------

def liste(request):
    """Affiche toutes les équipes et le formulaire de création."""
    contexte = {
        "equipes": EquipeRepository.get_all(),
        "form": NomEquipeForm(),
        "taille_max": TAILLE_MAX_EQUIPE,
    }
    return render(request, "equipes/liste.html", contexte)


def detail(request, equipe_id):
    """Affiche une équipe avec ses Pokémon et les formulaires de modification."""
    equipe = _get_equipe_ou_404(equipe_id)
    contexte = {
        "equipe": equipe,
        "pokemons": equipe.pokemons.all(),
        "form_nom": NomEquipeForm(initial={"nom": equipe.nom}),
        "form_ajout": AjoutPokemonForm(),
        "taille_max": TAILLE_MAX_EQUIPE,
    }
    return render(request, "equipes/detail.html", contexte)


# ---------- Actions sur l'équipe ----------

@require_POST
def creer(request):
    form = NomEquipeForm(request.POST)
    if not form.is_valid():
        _afficher_erreurs(request, form.errors)
        return redirect("equipes:liste")
    try:
        equipe = EquipeRepository.creer(form.cleaned_data["nom"])
    except ValidationError as e:
        _afficher_erreurs(request, e)
        return redirect("equipes:liste")
    messages.success(request, f"L'équipe « {equipe.nom} » a été créée.")
    return redirect("equipes:detail", equipe_id=equipe.pk)


@require_POST
def renommer(request, equipe_id):
    equipe = _get_equipe_ou_404(equipe_id)
    form = NomEquipeForm(request.POST)
    if not form.is_valid():
        _afficher_erreurs(request, form.errors)
        return redirect("equipes:detail", equipe_id=equipe.pk)
    try:
        EquipeRepository.renommer(equipe, form.cleaned_data["nom"])
    except ValidationError as e:
        _afficher_erreurs(request, e)
    else:
        messages.success(request, f"L'équipe s'appelle maintenant « {equipe.nom} ».")
    return redirect("equipes:detail", equipe_id=equipe.pk)


@require_POST
def supprimer(request, equipe_id):
    equipe = _get_equipe_ou_404(equipe_id)
    nom = equipe.nom
    EquipeRepository.supprimer(equipe)
    messages.success(request, f"L'équipe « {nom} » a été supprimée.")
    return redirect("equipes:liste")


# ---------- Actions sur les Pokémon de l'équipe ----------

@require_POST
def ajouter(request, equipe_id):
    equipe = _get_equipe_ou_404(equipe_id)
    form = AjoutPokemonForm(request.POST)
    if not form.is_valid():
        _afficher_erreurs(request, form.errors)
        return redirect("equipes:detail", equipe_id=equipe.pk)
    try:
        pokemon = EquipeRepository.ajouter_pokemon(equipe, form.cleaned_data["pokemon"].numero)
    except ValidationError as e:
        _afficher_erreurs(request, e)
    else:
        messages.success(request, f"{pokemon.nom.capitalize()} a rejoint l'équipe.")
    return redirect("equipes:detail", equipe_id=equipe.pk)


@require_POST
def retirer(request, equipe_id, numero):
    equipe = _get_equipe_ou_404(equipe_id)
    try:
        pokemon = EquipeRepository.retirer_pokemon(equipe, numero)
    except ValidationError as e:
        _afficher_erreurs(request, e)
    else:
        messages.success(request, f"{pokemon.nom.capitalize()} a quitté l'équipe.")
    return redirect("equipes:detail", equipe_id=equipe.pk)


@require_POST
def ajouter_depuis_fiche(request, numero):
    """Bouton « Ajouter à l'équipe » de la fiche d'un Pokémon.
    Revient ensuite sur la fiche, où le message s'affiche."""
    form = ChoixEquipeForm(request.POST)
    if not form.is_valid():
        _afficher_erreurs(request, form.errors)
        return redirect("fiche", numero=numero)
    equipe = form.cleaned_data["equipe"]
    try:
        pokemon = EquipeRepository.ajouter_pokemon(equipe, numero)
    except ValidationError as e:
        _afficher_erreurs(request, e)
    else:
        messages.success(request, f"{pokemon.nom.capitalize()} a rejoint l'équipe « {equipe.nom} ».")
    return redirect("fiche", numero=numero)
