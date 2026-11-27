
import requests

from pokemon.DTOs.pokemonDtos import PokemonDto


class PokeaApiService:
    BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

    @staticmethod
    def getPokemonByNumber(numero: int) -> PokemonDto:
        response = requests.get(
            f"{PokeaApiService.BASE_URL}{numero}",
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        return PokemonDto(
            numero=data["id"],
            nom=data["name"],
            image=data["sprites"]["front_default"],
            types=[t["type"]["name"] for t in data["types"]],
            stats={s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            taille=data["height"],
            poids=data["weight"],
            capacites=[c["ability"]["name"] for c in data["abilities"]]
        )

    @staticmethod
    def getAllPokemons() -> list[PokemonDto]:

        response = requests.get(
            f"{PokeaApiService.BASE_URL}?limit=251",
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        pokemons = []

        for pokemon in data["results"]:
            numero = int(pokemon["url"].rstrip("/").split("/")[-1])

            pokemons.append(
                PokeaApiService.getPokemonByNumber(numero)
            )

        return pokemons
