import requests
from django.core.management.base import BaseCommand

from pokemon.PokemonRepository.pokemonRepository import PokemonRepository
from pokemon.services.pokeaApiService import PokeaApiService


class Command(BaseCommand):
    help = "Récupère les Pokémon depuis la PokéAPI et les enregistre en base."

    def add_arguments(self, parser):
        parser.add_argument("--start", type=int, default=1, help="Premier numéro (défaut : 1)")
        parser.add_argument("--end", type=int, default=251, help="Dernier numéro (défaut : 251)")

    def handle(self, *args, **options):
        start, end = options["start"], options["end"]
        created_count = updated_count = error_count = 0

        for numero in range(start, end + 1):
            try:
                dto = PokeaApiService.getPokemonByNumber(numero)
                _, created = PokemonRepository.save(dto)
            except requests.RequestException as e:
                error_count += 1
                self.stderr.write(self.style.ERROR(f"#{numero} : erreur API ({e})"))
                continue

            if created:
                created_count += 1
            else:
                updated_count += 1
            self.stdout.write(f"#{dto.numero} {dto.nom} {'créé' if created else 'mis à jour'}")

        self.stdout.write(self.style.SUCCESS(
            f"Terminé : {created_count} créés, {updated_count} mis à jour, {error_count} erreurs."
        ))
