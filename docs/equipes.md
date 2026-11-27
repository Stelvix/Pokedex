# Gestion des équipes (Personne C — Alec)

Cette partie permet de **composer des équipes de Pokémon** : on crée une équipe, on lui donne un nom, on y ajoute **jusqu'à 5 Pokémon** du Pokédex, on la modifie et on la supprime. Tout est **enregistré dans la base SQLite**.

Elle utilise les Pokémon chargés par la partie données (`Steeven`, voir [donnees.md](donnees.md)) et reprend le gabarit et le thème de l'interface (`Tifenn`).

---

## 1. Ce que l'on peut faire

| Fonction | Où sur le site |
|----------|----------------|
| Créer une équipe et lui donner un nom | Page **Mes équipes** → « Nouvelle équipe » |
| Afficher toutes les équipes | Page **Mes équipes** (une carte par équipe, avec ses Pokémon) |
| Ajouter un Pokémon | Page de l'équipe → « Ajouter un Pokémon », **ou** depuis la fiche d'un Pokémon → « Ajouter à l'équipe » |
| Retirer un Pokémon | Page de l'équipe → bouton « Retirer » sous le Pokémon |
| Renommer une équipe | Page de l'équipe → « Modifier l'équipe » |
| Supprimer une équipe | Page de l'équipe → « Supprimer l'équipe » (une confirmation est demandée) |

On accède à tout ça avec le bouton **Mes équipes** de l'en-tête, ou directement sur <http://127.0.0.1:8000/equipes/>.

---

## 2. Installation

Il faut d'abord avoir suivi l'installation de [donnees.md](donnees.md) (environnement virtuel, `pip install -r requirements.txt`, `import_pokemons`). Ensuite :

```bash
# Crée les tables des équipes dans db.sqlite3 (à faire une fois après avoir récupéré la branche)
python manage.py migrate

# Lance le site
python manage.py runserver
```

Aucune nouvelle dépendance : tout est fait avec Django.

---

## 3. Les règles

| Règle | Message affiché si elle n'est pas respectée |
|-------|---------------------------------------------|
| **5 Pokémon maximum** par équipe | « L'équipe est complète : 5 Pokémon maximum. » |
| Pas deux fois le **même Pokémon** dans une équipe | « Pikachu est déjà dans l'équipe. » |
| Le **nom est obligatoire** (les espaces autour sont enlevés) | « Le nom de l'équipe est obligatoire. » |
| Le nom fait **50 caractères maximum** | « Le nom ne doit pas dépasser 50 caractères. » |
| Le nom est **unique**, sans tenir compte des majuscules (« Team Rocket » = « team rocket ») | « Une équipe s'appelle déjà « … ». » |
| On ne retire que des Pokémon **présents** dans l'équipe | « Pikachu n'est pas dans l'équipe. » |

Autres points :

- Un même Pokémon peut être dans **plusieurs équipes** différentes.
- **Retirer** un Pokémon d'une équipe ou **supprimer** une équipe ne supprime **jamais** le Pokémon du Pokédex.
- Quand une équipe est pleine, le formulaire d'ajout disparaît de sa page, et sur la fiche d'un Pokémon elle apparaît **grisée** dans la liste (« complète » ou « déjà dedans »).

---

## 4. Comment ça marche

### Le chemin d'une action

```
Page du site  ──►  Vue        ──►  Repository          ──►  Modèle          ──►  Base SQLite
(un bouton)       (views.py)      (vérifie le nom,         (règle des 5,         (db.sqlite3)
                                   trouve le Pokémon)       pas de doublon)
```

1. Chaque bouton envoie un **formulaire** (méthode POST) vers sa propre **vue** (créer, renommer, supprimer, ajouter, retirer).
2. La vue vérifie le formulaire, puis demande au **repository** de faire l'action.
3. Le repository vérifie le nom et va chercher le Pokémon par son numéro ; le **modèle** vérifie la règle des 5 et les doublons.
4. Si quelque chose ne va pas, une `ValidationError` est levée avec un message en français. La vue l'affiche en **message rouge** ; sinon elle affiche un **message vert** (« Pikachu a rejoint l'équipe. »).
5. La vue **redirige** ensuite vers la page de l'équipe (ou vers la fiche du Pokémon si on vient de la fiche).

> Les actions n'acceptent que POST : on ne peut pas supprimer une équipe juste en ouvrant un lien.

### Les fichiers

Tout est dans le dossier `equipes/` (une app Django à part, pour ne pas mélanger avec le code des autres) :

| Fichier | Rôle |
|---------|------|
| `equipes/models.py` | Le modèle `Equipe` et ses règles (`ajouter_pokemon`, `retirer_pokemon`, limite de 5) |
| `equipes/Repository/equipeRepository.py` | Toutes les opérations sur les équipes (créer, renommer, supprimer, ajouter, retirer, lire) |
| `equipes/forms.py` | Les formulaires : nom de l'équipe, choix du Pokémon, choix de l'équipe (fiche) |
| `equipes/views.py` | Les pages et les actions des boutons |
| `equipes/urls.py` | Les adresses (voir plus bas) |
| `equipes/templates/equipes/` | Les pages : `liste.html`, `detail.html`, l'encadré de la fiche et les messages |
| `equipes/templatetags/equipes_tags.py` | La balise `{% ajout_equipe pokemon %}` qui affiche l'encadré « Équipes » sur la fiche |
| `equipes/static/equipes/css/equipes.css` | Le style des équipes (classes `eq-…`) |
| `equipes/migrations/0001_initial.py` | La création des tables dans la base |

### Les adresses

| Adresse | Méthode | Ce qu'elle fait |
|---------|---------|-----------------|
| `/equipes/` | GET | Page : toutes les équipes + création |
| `/equipes/<id>/` | GET | Page : une équipe, ses Pokémon, modification |
| `/equipes/creer/` | POST | Crée une équipe |
| `/equipes/<id>/renommer/` | POST | Renomme l'équipe |
| `/equipes/<id>/supprimer/` | POST | Supprime l'équipe |
| `/equipes/<id>/ajouter/` | POST | Ajoute le Pokémon choisi |
| `/equipes/<id>/retirer/<numero>/` | POST | Retire le Pokémon n°`numero` |
| `/equipes/pokemon/<numero>/ajouter/` | POST | Ajoute le Pokémon depuis sa fiche, puis revient sur la fiche |

Dans les templates, on les utilise avec le préfixe `equipes:`, par exemple `{% url 'equipes:liste' %}`.

---

## 5. Sauvegarde dans SQLite

Les équipes sont rangées dans **deux tables**, créées par `python manage.py migrate` :

```
equipe                         equipe_pokemons                    pokemon
──────────────────             ─────────────────────              ──────────────
id                    ◄──────  equipe_id                          id
nom (unique, 50 car.)          pokemon_id            ──────►      numero, nom, ...
date_creation
```

- **`equipe`** : une ligne par équipe (son nom et sa date de création).
- **`equipe_pokemons`** : une ligne par Pokémon dans une équipe. C'est un lien « plusieurs à plusieurs » (`ManyToManyField`) : une équipe a plusieurs Pokémon, et un Pokémon peut être dans plusieurs équipes.
- Quand on supprime une équipe, ses lignes dans `equipe_pokemons` sont supprimées aussi, mais les Pokémon restent dans `pokemon`.

| Champ du modèle | Exemple | Remarque |
|-----------------|---------|----------|
| `nom` | `"Team Rocket"` | Unique, 50 caractères maximum |
| `pokemons` | Meowth, Koffing, Weezing | 0 à 5 Pokémon, toujours affichés par numéro |
| `date_creation` | `2026-11-27 16:25` | Remplie automatiquement à la création |

> Comme pour les Pokémon, `db.sqlite3` n'est **pas envoyé sur GitHub** : les équipes créées restent sur l'ordinateur de chacun.

---

## 6. Utiliser les équipes dans le code

Toutes les opérations passent par le repository :

```python
from django.core.exceptions import ValidationError
from equipes.Repository.equipeRepository import EquipeRepository

equipe = EquipeRepository.creer("Team Rocket")      # crée une équipe vide
EquipeRepository.ajouter_pokemon(equipe, 52)         # ajoute Meowth (par son numéro)
EquipeRepository.retirer_pokemon(equipe, 52)         # le retire
EquipeRepository.renommer(equipe, "Rocket")          # change le nom
EquipeRepository.get_all()                           # toutes les équipes, triées par nom
EquipeRepository.get_by_id(1)                        # une équipe (ou None)

# En cas de problème, une ValidationError est levée avec un message en français
for numero in (1, 4, 7, 25, 52):
    EquipeRepository.ajouter_pokemon(equipe, numero)  # l'équipe est maintenant pleine
try:
    EquipeRepository.ajouter_pokemon(equipe, 150)
except ValidationError as e:
    print(e.messages[0])   # « L'équipe est complète : 5 Pokémon maximum. »

EquipeRepository.supprimer(equipe)                   # supprime l'équipe (pas les Pokémon)
```

> Il faut toujours passer par `ajouter_pokemon` (du repository ou du modèle) : un `equipe.pokemons.add(...)` direct ne vérifierait pas la limite de 5.

---

## 7. Fichiers modifiés en dehors de `equipes/`

Pour brancher les équipes au reste du site, quelques lignes ont été ajoutées dans des fichiers communs :

| Fichier | Ajout |
|---------|-------|
| `pokedex/settings.py` | `'equipes'` dans `INSTALLED_APPS` |
| `pokedex/urls.py` | `path('equipes/', include('equipes.urls'))` |
| `pokemon/templates/pokemon/base.html` | Le lien vers `equipes.css` et le bouton **Mes équipes** dans l'en-tête |
| `pokemon/templates/pokemon/fiche.html` | `{% load equipes_tags %}` et `{% ajout_equipe pokemon %}` sous les statistiques |

---

## 8. Problèmes fréquents

| Problème | Solution |
|----------|----------|
| `no such table: equipe` | Lancer `python manage.py migrate` |
| La liste « Choisir un Pokémon » est vide | Les Pokémon ne sont pas chargés : lancer `python manage.py import_pokemons` |
| `'equipes_tags' is not a registered tag library` | Vérifier que `'equipes'` est dans `INSTALLED_APPS`, puis **redémarrer** `runserver` |
| Les pages des équipes n'ont pas de style | Redémarrer `runserver` (le dossier `equipes/static/` est nouveau) et rafraîchir avec Ctrl + F5 |
| Un message rouge s'affiche | C'est une règle qui n'est pas respectée (voir la partie 3) : rien n'a été modifié |
