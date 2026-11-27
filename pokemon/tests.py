from django.test import TestCase

from pokemon.services.pokeaApiService import PokeaApiService


class PokeaApiServiceTest(TestCase):

    def test_get_all_pokemons(self):
        pokemons = PokeaApiService.getAllPokemons()

        print(f"Nombre de Pokémon : {len(pokemons)}")

        for pokemon in pokemons:
            print(pokemon.numero, pokemon.nom)
