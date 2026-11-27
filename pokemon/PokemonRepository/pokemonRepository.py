from pokemon.DTOs.pokemonDtos import PokemonDto
from pokemon.models import Pokemon


class PokemonRepository:

    @staticmethod
    def save(dto: PokemonDto) -> tuple[Pokemon, bool]:
        """Crée ou met à jour un Pokémon à partir de son numéro.
        Retourne (pokemon, created)."""
        return Pokemon.objects.update_or_create(
            numero=dto.numero,
            defaults={
                "nom": dto.nom,
                "image": dto.image or "",
                "types": dto.types,
                "stats": dto.stats,
                "taille": dto.taille,
                "poids": dto.poids,
                "capacites": dto.capacites,
            },
        )

    @staticmethod
    def get_all() -> list[Pokemon]:
        return list(Pokemon.objects.all())

    @staticmethod
    def get_by_numero(numero: int) -> Pokemon | None:
        return Pokemon.objects.filter(numero=numero).first()
