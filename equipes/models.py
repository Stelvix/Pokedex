from django.core.exceptions import ValidationError
from django.db import models

from pokemon.models import Pokemon

# Nombre maximum de Pokémon dans une équipe
TAILLE_MAX_EQUIPE = 5


class Equipe(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    pokemons = models.ManyToManyField(Pokemon, related_name="equipes", blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        db_table = "equipe"
        verbose_name = "Équipe"
        verbose_name_plural = "Équipes"
        ordering = ["nom"]

    def nb_pokemons(self) -> int:
        return self.pokemons.count()

    def est_complete(self) -> bool:
        return self.nb_pokemons() >= TAILLE_MAX_EQUIPE

    def ajouter_pokemon(self, pokemon: Pokemon) -> None:
        """Ajoute un Pokémon à l'équipe.
        Lève une ValidationError si l'équipe est pleine ou si le Pokémon y est déjà."""
        if self.pokemons.filter(pk=pokemon.pk).exists():
            raise ValidationError(f"{pokemon.nom.capitalize()} est déjà dans l'équipe.")
        if self.est_complete():
            raise ValidationError(
                f"L'équipe est complète : {TAILLE_MAX_EQUIPE} Pokémon maximum."
            )
        self.pokemons.add(pokemon)

    def retirer_pokemon(self, pokemon: Pokemon) -> None:
        """Retire un Pokémon de l'équipe (le Pokémon reste dans le Pokédex)."""
        self.pokemons.remove(pokemon)
