from django.core.exceptions import ValidationError

from equipes.models import Equipe, LONGUEUR_MAX_NOM
from pokemon.models import Pokemon
from pokemon.Repository.pokemonRepository import PokemonRepository


class EquipeRepository:
    """Toutes les opérations sur les équipes passent par ici.
    En cas de problème (nom déjà pris, équipe pleine...), une ValidationError
    est levée avec un message en français prêt à être affiché."""

    # ---------- Lecture ----------

    @staticmethod
    def get_all() -> list[Equipe]:
        """Toutes les équipes, triées par nom, avec leurs Pokémon."""
        return list(Equipe.objects.prefetch_related("pokemons"))

    @staticmethod
    def get_by_id(equipe_id: int) -> Equipe | None:
        return Equipe.objects.filter(pk=equipe_id).first()

    # ---------- Équipe ----------

    @staticmethod
    def creer(nom: str) -> Equipe:
        """Crée une équipe vide avec le nom donné."""
        nom = EquipeRepository._valider_nom(nom)
        return Equipe.objects.create(nom=nom)

    @staticmethod
    def renommer(equipe: Equipe, nom: str) -> Equipe:
        equipe.nom = EquipeRepository._valider_nom(nom, equipe)
        equipe.save(update_fields=["nom"])
        return equipe

    @staticmethod
    def supprimer(equipe: Equipe) -> None:
        """Supprime l'équipe. Ses Pokémon restent dans le Pokédex."""
        equipe.delete()

    # ---------- Pokémon de l'équipe ----------

    @staticmethod
    def ajouter_pokemon(equipe: Equipe, numero: int) -> Pokemon:
        """Ajoute le Pokémon n°numero à l'équipe (5 maximum, pas de doublon).
        Retourne le Pokémon ajouté."""
        pokemon = EquipeRepository._get_pokemon(numero)
        equipe.ajouter_pokemon(pokemon)
        return pokemon

    @staticmethod
    def retirer_pokemon(equipe: Equipe, numero: int) -> Pokemon:
        """Retire le Pokémon n°numero de l'équipe. Retourne le Pokémon retiré."""
        pokemon = EquipeRepository._get_pokemon(numero)
        equipe.retirer_pokemon(pokemon)
        return pokemon

    # ---------- Outils internes ----------

    @staticmethod
    def _get_pokemon(numero: int) -> Pokemon:
        pokemon = PokemonRepository.get_by_numero(numero)
        if pokemon is None:
            raise ValidationError(f"Aucun Pokémon n°{numero} dans le Pokédex.")
        return pokemon

    @staticmethod
    def _valider_nom(nom: str, equipe: Equipe | None = None) -> str:
        """Nettoie le nom et vérifie qu'il est valide.
        `equipe` : l'équipe qu'on renomme (pour ne pas la compter comme doublon)."""
        nom = (nom or "").strip()
        if not nom:
            raise ValidationError("Le nom de l'équipe est obligatoire.")
        # SQLite ne vérifie pas la longueur max d'un texte : on le fait ici
        if len(nom) > LONGUEUR_MAX_NOM:
            raise ValidationError(
                f"Le nom ne doit pas dépasser {LONGUEUR_MAX_NOM} caractères."
            )
        # Nom unique, sans tenir compte des majuscules ("Rocket" = "rocket")
        doublons = Equipe.objects.filter(nom__iexact=nom)
        if equipe is not None:
            doublons = doublons.exclude(pk=equipe.pk)
        if doublons.exists():
            raise ValidationError(f"Une équipe s'appelle déjà « {nom} ».")
        return nom
