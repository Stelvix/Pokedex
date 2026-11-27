from typing import List

from django.db import models

# Create your models here.
class Pokemon(models.Model):
    nom = models.CharField(max_length=100)
    numero = models.PositiveIntegerField(unique=True)
    image = models.URLField(max_length=500)

    types = models.JSONField(default=list)
    stats = models.JSONField(default=dict)

    taille = models.IntegerField(default=0)
    poids = models.IntegerField(default=0)
    capacites = models.JSONField(default=list)

    def __str__(self):
        return self.nom
    class Meta:
        db_table = 'pokemon'
        verbose_name = 'Pokemon'
        verbose_name_plural = 'Pokemons'
        ordering = ['numero']