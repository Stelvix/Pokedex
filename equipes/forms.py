from django import forms

from equipes.models import Equipe, LONGUEUR_MAX_NOM
from pokemon.models import Pokemon


class NomEquipeForm(forms.Form):
    """Formulaire du nom : sert à créer une équipe et à la renommer."""
    nom = forms.CharField(
        label="Nom de l'équipe",
        max_length=LONGUEUR_MAX_NOM,
        error_messages={
            "required": "Le nom de l'équipe est obligatoire.",
            "max_length": f"Le nom ne doit pas dépasser {LONGUEUR_MAX_NOM} caractères.",
        },
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ex. : Team Rocket",
        }),
    )


class PokemonChoiceField(forms.ModelChoiceField):
    """Liste déroulante des Pokémon, affichés comme « #025 – Pikachu »."""
    def label_from_instance(self, pokemon):
        return f"#{pokemon.numero:03d} – {pokemon.nom.capitalize()}"


class AjoutPokemonForm(forms.Form):
    """Formulaire pour choisir un Pokémon à ajouter dans une équipe."""
    pokemon = PokemonChoiceField(
        label="Pokémon à ajouter",
        queryset=Pokemon.objects.all(),
        to_field_name="numero",  # la valeur envoyée est le numéro du Pokémon
        empty_label="Choisir un Pokémon…",
        error_messages={
            "required": "Il faut choisir un Pokémon.",
            "invalid_choice": "Ce Pokémon n'existe pas dans le Pokédex.",
        },
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class ChoixEquipeForm(forms.Form):
    """Formulaire de la fiche d'un Pokémon : choisir l'équipe où l'ajouter.
    La liste déroulante est écrite à la main dans _ajout_depuis_fiche.html
    (pour griser les équipes pleines) ; ce formulaire sert à vérifier le choix."""
    equipe = forms.ModelChoiceField(
        queryset=Equipe.objects.all(),
        error_messages={
            "required": "Il faut choisir une équipe.",
            "invalid_choice": "Cette équipe n'existe pas.",
        },
    )
