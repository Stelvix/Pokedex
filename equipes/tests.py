"""Tests de la gestion des équipes.

Lancer :  python manage.py test equipes

Django crée une base de test vide à chaque lancement (ta vraie base n'est pas touchée)
et il n'y a pas d'appel à PokéAPI : les tests créent eux-mêmes quelques Pokémon.
"""
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from equipes.models import Equipe, TAILLE_MAX_EQUIPE
from equipes.Repository.equipeRepository import EquipeRepository
from pokemon.models import Pokemon

NOMS = ["bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard", "squirtle"]


def creer_pokemons():
    """Crée les Pokémon n°1 à 7 dans la base de test."""
    for numero, nom in enumerate(NOMS, start=1):
        Pokemon.objects.create(
            numero=numero,
            nom=nom,
            image=f"https://example.com/{numero}.png",
            types=["grass"],
            stats={"hp": 45, "attack": 49, "defense": 49,
                   "special-attack": 65, "special-defense": 65, "speed": 45},
            taille=7,
            poids=69,
            capacites=["overgrow"],
        )


def messages_de(response):
    """Les messages (réussite / erreur) ajoutés pendant la requête."""
    return [str(m) for m in get_messages(response.wsgi_request)]


# ---------------------------------------------------------------------------
# Modèle : règles de l'équipe
# ---------------------------------------------------------------------------

class EquipeModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        creer_pokemons()

    def setUp(self):
        self.equipe = Equipe.objects.create(nom="Team Test")

    def pokemon(self, numero):
        return Pokemon.objects.get(numero=numero)

    def test_une_nouvelle_equipe_est_vide(self):
        self.assertEqual(self.equipe.nb_pokemons(), 0)
        self.assertFalse(self.equipe.est_complete())
        self.assertEqual(len(self.equipe.places_libres()), TAILLE_MAX_EQUIPE)

    def test_ajouter_un_pokemon(self):
        self.equipe.ajouter_pokemon(self.pokemon(1))
        self.assertEqual(list(self.equipe.pokemons.all()), [self.pokemon(1)])
        self.assertEqual(len(self.equipe.places_libres()), TAILLE_MAX_EQUIPE - 1)

    def test_limite_de_5_pokemons(self):
        for numero in range(1, 6):
            self.equipe.ajouter_pokemon(self.pokemon(numero))
        self.assertTrue(self.equipe.est_complete())
        self.assertEqual(len(self.equipe.places_libres()), 0)

        with self.assertRaisesMessage(ValidationError, "5 Pokémon maximum"):
            self.equipe.ajouter_pokemon(self.pokemon(6))
        self.assertEqual(self.equipe.nb_pokemons(), 5)

    def test_pas_deux_fois_le_meme_pokemon(self):
        self.equipe.ajouter_pokemon(self.pokemon(1))
        with self.assertRaisesMessage(ValidationError, "déjà dans l'équipe"):
            self.equipe.ajouter_pokemon(self.pokemon(1))
        self.assertEqual(self.equipe.nb_pokemons(), 1)

    def test_retirer_un_pokemon(self):
        self.equipe.ajouter_pokemon(self.pokemon(1))
        self.equipe.retirer_pokemon(self.pokemon(1))
        self.assertEqual(self.equipe.nb_pokemons(), 0)
        # le Pokémon est toujours dans le Pokédex
        self.assertTrue(Pokemon.objects.filter(numero=1).exists())

    def test_retirer_un_pokemon_absent(self):
        with self.assertRaisesMessage(ValidationError, "n'est pas dans l'équipe"):
            self.equipe.retirer_pokemon(self.pokemon(1))

    def test_un_pokemon_peut_etre_dans_plusieurs_equipes(self):
        autre = Equipe.objects.create(nom="Autre")
        self.equipe.ajouter_pokemon(self.pokemon(1))
        autre.ajouter_pokemon(self.pokemon(1))
        self.assertEqual(self.pokemon(1).equipes.count(), 2)


# ---------------------------------------------------------------------------
# Repository : création, nom, ajout / retrait, sauvegarde
# ---------------------------------------------------------------------------

class EquipeRepositoryTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        creer_pokemons()

    # --- Création et nom ---

    def test_creer_une_equipe(self):
        equipe = EquipeRepository.creer("  Team Rocket  ")
        self.assertEqual(equipe.nom, "Team Rocket")  # espaces enlevés
        self.assertTrue(Equipe.objects.filter(nom="Team Rocket").exists())

    def test_nom_obligatoire(self):
        for nom in ("", "   ", None):
            with self.assertRaisesMessage(ValidationError, "obligatoire"):
                EquipeRepository.creer(nom)
        self.assertEqual(Equipe.objects.count(), 0)

    def test_nom_trop_long(self):
        EquipeRepository.creer("x" * 50)  # 50 caractères : accepté
        with self.assertRaisesMessage(ValidationError, "50 caractères"):
            EquipeRepository.creer("y" * 51)

    def test_nom_unique_sans_tenir_compte_des_majuscules(self):
        EquipeRepository.creer("Team Rocket")
        with self.assertRaisesMessage(ValidationError, "s'appelle déjà"):
            EquipeRepository.creer("TEAM rocket")
        self.assertEqual(Equipe.objects.count(), 1)

    def test_renommer(self):
        equipe = EquipeRepository.creer("Team Rocket")
        EquipeRepository.renommer(equipe, "Rocket")
        equipe.refresh_from_db()
        self.assertEqual(equipe.nom, "Rocket")

    def test_renommer_avec_le_meme_nom_en_majuscules(self):
        equipe = EquipeRepository.creer("Team Rocket")
        EquipeRepository.renommer(equipe, "TEAM ROCKET")  # pas un doublon de lui-même
        equipe.refresh_from_db()
        self.assertEqual(equipe.nom, "TEAM ROCKET")

    def test_renommer_avec_un_nom_deja_pris(self):
        EquipeRepository.creer("Les Pros")
        equipe = EquipeRepository.creer("Team Rocket")
        with self.assertRaisesMessage(ValidationError, "s'appelle déjà"):
            EquipeRepository.renommer(equipe, "les pros")
        equipe.refresh_from_db()
        self.assertEqual(equipe.nom, "Team Rocket")

    # --- Lecture et suppression ---

    def test_get_all_trie_par_nom(self):
        for nom in ("Zèbre", "Alpha", "Milieu"):
            EquipeRepository.creer(nom)
        self.assertEqual([e.nom for e in EquipeRepository.get_all()], ["Alpha", "Milieu", "Zèbre"])

    def test_get_by_id(self):
        equipe = EquipeRepository.creer("Team Rocket")
        self.assertEqual(EquipeRepository.get_by_id(equipe.pk), equipe)
        self.assertIsNone(EquipeRepository.get_by_id(9999))

    def test_supprimer_garde_les_pokemons(self):
        equipe = EquipeRepository.creer("Team Rocket")
        EquipeRepository.ajouter_pokemon(equipe, 1)
        EquipeRepository.supprimer(equipe)
        self.assertEqual(Equipe.objects.count(), 0)
        self.assertEqual(Pokemon.objects.count(), len(NOMS))

    # --- Pokémon de l'équipe ---

    def test_ajouter_et_retirer_par_numero(self):
        equipe = EquipeRepository.creer("Team Rocket")
        pokemon = EquipeRepository.ajouter_pokemon(equipe, 4)
        self.assertEqual(pokemon.nom, "charmander")
        self.assertEqual(equipe.nb_pokemons(), 1)

        EquipeRepository.retirer_pokemon(equipe, 4)
        self.assertEqual(equipe.nb_pokemons(), 0)

    def test_ajouter_un_numero_inexistant(self):
        equipe = EquipeRepository.creer("Team Rocket")
        with self.assertRaisesMessage(ValidationError, "Aucun Pokémon n°999"):
            EquipeRepository.ajouter_pokemon(equipe, 999)

    def test_la_limite_de_5_passe_aussi_par_le_repository(self):
        equipe = EquipeRepository.creer("Team Rocket")
        for numero in range(1, 6):
            EquipeRepository.ajouter_pokemon(equipe, numero)
        with self.assertRaisesMessage(ValidationError, "5 Pokémon maximum"):
            EquipeRepository.ajouter_pokemon(equipe, 6)

    def test_sauvegarde_dans_la_base(self):
        """Ce qui est fait est bien enregistré : on relit tout depuis la base."""
        equipe = EquipeRepository.creer("Team Rocket")
        for numero in (1, 4, 7):
            EquipeRepository.ajouter_pokemon(equipe, numero)

        relue = Equipe.objects.get(pk=equipe.pk)  # nouvelle lecture SQLite
        self.assertEqual(relue.nom, "Team Rocket")
        self.assertEqual([p.numero for p in relue.pokemons.all()], [1, 4, 7])


# ---------------------------------------------------------------------------
# Vues : les pages et les boutons, comme un vrai visiteur
# ---------------------------------------------------------------------------

class EquipeVuesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        creer_pokemons()

    def setUp(self):
        self.equipe = EquipeRepository.creer("Team Rocket")

    def url(self, nom, *args):
        return reverse(f"equipes:{nom}", args=args)

    # --- Pages ---

    def test_page_liste(self):
        EquipeRepository.ajouter_pokemon(self.equipe, 1)
        r = self.client.get(self.url("liste"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "equipes/liste.html")
        self.assertContains(r, "Team Rocket")
        self.assertContains(r, "1/5")

    def test_page_liste_sans_equipe(self):
        self.equipe.delete()
        r = self.client.get(self.url("liste"))
        self.assertContains(r, "Aucune équipe pour l")

    def test_page_liste_ne_fait_pas_une_requete_par_equipe(self):
        for i in range(5):
            equipe = EquipeRepository.creer(f"Équipe {i}")
            EquipeRepository.ajouter_pokemon(equipe, 1)
        with self.assertNumQueries(2):  # 1 pour les équipes + 1 pour tous leurs Pokémon
            self.client.get(self.url("liste"))

    def test_page_detail(self):
        EquipeRepository.ajouter_pokemon(self.equipe, 4)
        r = self.client.get(self.url("detail", self.equipe.pk))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "equipes/detail.html")
        self.assertContains(r, "Charmander")
        self.assertContains(r, "Place libre", count=4)

    def test_page_detail_equipe_inexistante(self):
        r = self.client.get(self.url("detail", 9999))
        self.assertEqual(r.status_code, 404)

    def test_page_detail_equipe_complete(self):
        for numero in range(1, 6):
            EquipeRepository.ajouter_pokemon(self.equipe, numero)
        r = self.client.get(self.url("detail", self.equipe.pk))
        self.assertContains(r, "L'équipe est complète")
        self.assertNotContains(r, 'name="pokemon"')  # plus de formulaire d'ajout

    def test_lien_mes_equipes_dans_l_en_tete(self):
        r = self.client.get(reverse("accueil"))
        self.assertContains(r, f'href="{self.url("liste")}"')

    # --- Actions ---

    def test_les_actions_refusent_get(self):
        """Supprimer, ajouter, etc. ne se font pas en ouvrant un simple lien."""
        for url in (self.url("creer"),
                    self.url("supprimer", self.equipe.pk),
                    self.url("ajouter", self.equipe.pk),
                    self.url("retirer", self.equipe.pk, 1)):
            self.assertEqual(self.client.get(url).status_code, 405)
        self.assertTrue(Equipe.objects.filter(pk=self.equipe.pk).exists())

    def test_creer(self):
        r = self.client.post(self.url("creer"), {"nom": "Les Pros"})
        equipe = Equipe.objects.get(nom="Les Pros")
        self.assertRedirects(r, self.url("detail", equipe.pk))
        self.assertIn("L'équipe « Les Pros » a été créée.", messages_de(r))

    def test_creer_avec_un_nom_invalide(self):
        r = self.client.post(self.url("creer"), {"nom": ""})
        self.assertRedirects(r, self.url("liste"))
        self.assertIn("Le nom de l'équipe est obligatoire.", messages_de(r))

        r = self.client.post(self.url("creer"), {"nom": "team rocket"})
        self.assertIn("Une équipe s'appelle déjà « team rocket ».", messages_de(r))
        self.assertEqual(Equipe.objects.count(), 1)

    def test_renommer(self):
        r = self.client.post(self.url("renommer", self.equipe.pk), {"nom": "Rocket"})
        self.assertRedirects(r, self.url("detail", self.equipe.pk))
        self.equipe.refresh_from_db()
        self.assertEqual(self.equipe.nom, "Rocket")

    def test_supprimer(self):
        r = self.client.post(self.url("supprimer", self.equipe.pk))
        self.assertRedirects(r, self.url("liste"))
        self.assertFalse(Equipe.objects.exists())

    def test_ajouter_puis_retirer(self):
        r = self.client.post(self.url("ajouter", self.equipe.pk), {"pokemon": 7})
        self.assertRedirects(r, self.url("detail", self.equipe.pk))
        self.assertIn("Squirtle a rejoint l'équipe.", messages_de(r))
        self.assertEqual(self.equipe.nb_pokemons(), 1)

        r = self.client.post(self.url("retirer", self.equipe.pk, 7))
        self.assertIn("Squirtle a quitté l'équipe.", messages_de(r))
        self.assertEqual(self.equipe.nb_pokemons(), 0)

    def test_ajouter_un_6e_pokemon_est_refuse(self):
        for numero in range(1, 6):
            self.client.post(self.url("ajouter", self.equipe.pk), {"pokemon": numero})
        r = self.client.post(self.url("ajouter", self.equipe.pk), {"pokemon": 6})
        self.assertIn("L'équipe est complète : 5 Pokémon maximum.", messages_de(r))
        self.assertEqual(self.equipe.nb_pokemons(), 5)

    def test_ajouter_sans_choisir_ou_numero_inconnu(self):
        r = self.client.post(self.url("ajouter", self.equipe.pk), {})
        self.assertIn("Il faut choisir un Pokémon.", messages_de(r))
        r = self.client.post(self.url("ajouter", self.equipe.pk), {"pokemon": 999})
        self.assertIn("Ce Pokémon n'existe pas dans le Pokédex.", messages_de(r))
        self.assertEqual(self.equipe.nb_pokemons(), 0)

    # --- Encadré « Équipes » de la fiche d'un Pokémon ---

    def test_fiche_affiche_l_encadre_equipes(self):
        EquipeRepository.ajouter_pokemon(self.equipe, 1)
        r = self.client.get(reverse("fiche", args=[1]))
        self.assertContains(r, "Fait partie de")
        self.assertContains(r, "Team Rocket (1/5) – déjà dedans")  # option grisée

    def test_ajouter_depuis_la_fiche(self):
        r = self.client.post(self.url("ajouter_depuis_fiche", 4), {"equipe": self.equipe.pk})
        self.assertRedirects(r, reverse("fiche", args=[4]))
        self.assertIn("Charmander a rejoint l'équipe « Team Rocket ».", messages_de(r))
        self.assertEqual(self.equipe.nb_pokemons(), 1)

    def test_ajouter_depuis_la_fiche_sans_equipe(self):
        r = self.client.post(self.url("ajouter_depuis_fiche", 4), {})
        self.assertRedirects(r, reverse("fiche", args=[4]))
        self.assertIn("Il faut choisir une équipe.", messages_de(r))
