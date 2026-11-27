# Données et recherche (Personne A — Steeven)

Cette partie s'occupe de **récupérer les Pokémon**, de **les ranger dans la base de données** et de **les mettre à disposition** du reste de l'application (l'interface, faite par la personne B).

---

## 1. Installation

### Ce qu'il faut avoir

- **Python 3.12 ou plus** (le projet tourne avec Python 3.14)
- Une connexion internet, **seulement pour le premier chargement** des Pokémon

### Étapes

```bash
# 1. Se placer dans le dossier du projet
cd Pokedex

# 2. Créer un environnement virtuel
python3 -m venv .venv

# 3. L'activer
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer la base de données (la table "pokemon")
python manage.py migrate

# 6. Charger les 251 Pokémon depuis PokéAPI (une seule fois)
python manage.py import_pokemons

# 7. Lancer le site
python manage.py runserver
```

Le site est ensuite visible sur <http://127.0.0.1:8000>.

---

## 2. Dépendances

| Paquet     | Version | À quoi il sert                                  |
|------------|---------|-------------------------------------------------|
| `Django`   | 5.2.19  | Le framework web, la base de données, les pages |
| `requests` | 2.34.2  | Faire les appels à PokéAPI                      |

Les deux sont listés dans `requirements.txt`.
La base **SQLite** est déjà incluse dans Python, il n'y a rien à installer en plus.

---

## 3. Comment marchent les données

### Le chemin d'un Pokémon

```
PokéAPI  ──►  Service  ──►  DTO  ──►  Repository  ──►  Base SQLite  ──►  Pages du site
(internet)   (récupère)   (trie)    (enregistre)      (db.sqlite3)     (personne B)
```

1. Le **service** va chercher le Pokémon sur PokéAPI.
2. Il garde seulement les infos utiles et les met dans un **DTO** (une petite boîte de données propre).
3. Le **repository** prend ce DTO et l'enregistre dans la base.
4. Les pages du site lisent ensuite **directement la base**, sans repasser par internet.

### Les fichiers

| Fichier | Rôle |
|---------|------|
| `pokemon/services/pokeaApiService.py` | Parle avec PokéAPI et transforme la réponse en DTO |
| `pokemon/DTOs/pokemonDtos.py` | Le DTO `PokemonDto` : la forme des données qu'on garde |
| `pokemon/models.py` | Le modèle `Pokemon` : la table dans la base |
| `pokemon/Repository/pokemonRepository.py` | Enregistre et relit les Pokémon dans la base |
| `pokemon/management/commands/import_pokemons.py` | Le script de chargement initial |

### Les informations gardées pour chaque Pokémon

| Champ       | Exemple (Pikachu)                         | Remarque |
|-------------|-------------------------------------------|----------|
| `numero`    | `25`                                      | Unique, sert d'identifiant |
| `nom`       | `"pikachu"`                               | Nom anglais, en minuscules (comme PokéAPI) |
| `image`     | `"https://raw.githubusercontent.com/..."` | Lien vers l'image |
| `types`     | `["electric"]`                            | Liste |
| `stats`     | `{"hp": 35, "attack": 55, ...}`           | PV, attaque, défense, att. spé., déf. spé., vitesse |
| `taille`    | `4`                                       | En **décimètres** (4 → 0,4 m) |
| `poids`     | `60`                                      | En **hectogrammes** (60 → 6 kg) |
| `capacites` | `["static", "lightning-rod"]`             | Liste |

> La taille et le poids sont gardés tels que PokéAPI les donne. La conversion en mètres et en kilos se fait au moment de l'affichage (dans `views.py`).

Les Pokémon sont toujours rangés **par numéro** (1, 2, 3…).

---

## 4. Le script de chargement

```bash
python manage.py import_pokemons
```

- Récupère les Pokémon **n°1 à n°251** et les enregistre dans la base.
- **On ne le lance qu'une fois.** Après, le site ne fait plus aucun appel à PokéAPI : tout est lu dans la base.
- On peut le relancer sans risque : un Pokémon déjà présent est **mis à jour**, pas ajouté en double.
- Si un Pokémon n'arrive pas à se charger (problème réseau), le script affiche l'erreur et **continue avec les suivants**.

À la fin, il affiche un résumé :

```
Terminé : 251 créés, 0 mis à jour, 0 erreurs.
```

**Charger seulement une partie** (pratique pour tester) :

```bash
python manage.py import_pokemons --start 1 --end 10
```

---

## 5. Utiliser les données dans le code

Le repository donne des fonctions simples pour lire la base :

```python
from pokemon.Repository.pokemonRepository import PokemonRepository

PokemonRepository.get_all()          # tous les Pokémon, triés par numéro
PokemonRepository.get_by_numero(25)  # Pikachu (ou None s'il n'existe pas)
```

---

## 6. Recherche et filtre

> ⚠️ **Pas encore fait dans le code.** Les fonctions ci-dessous sont celles prévues pour cette partie.

| Besoin | Ce que ça doit faire |
|--------|----------------------|
| Recherche par nom | Taper `pika` trouve `pikachu` (nom partiel, majuscules ignorées) |
| Recherche par numéro | Taper `25` trouve Pikachu |
| Filtre par type | Choisir `fire` affiche seulement les Pokémon de type feu |

---

## 7. Problèmes fréquents

| Problème | Solution |
|----------|----------|
| `no such table: pokemon` | Lancer `python manage.py migrate` |
| Le site est vide / page 404 sur une fiche | Lancer `python manage.py import_pokemons` |
| `ModuleNotFoundError: requests` | Lancer `pip install -r requirements.txt` (avec le `.venv` activé) |
| Erreurs API pendant l'import | Vérifier la connexion, puis relancer le script |

> Le fichier `db.sqlite3` n'est **pas envoyé sur GitHub** (il est dans le `.gitignore`). Chaque personne doit donc lancer `migrate` puis `import_pokemons` chez elle.
