from dataclasses import dataclass

@dataclass
class PokemonDto:
    numero:int
    nom:str
    image:str
    types:list
    stats:list
    taille:int
    poids:int
    capacites:list