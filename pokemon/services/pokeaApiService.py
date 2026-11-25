import requests

# import de mon DTO pokemon
from pokemon.DTOs.pokemonDtos import PokemonDto

class PokeaApiService:
    BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

    @staticmethod
    def getPokemonByNumber(numero: int) -> PokemonDto:
        response = requests.get(f"{PokeaApiService.BASE_URL}{numero}", timeout=10)