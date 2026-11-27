from django.urls import path

from equipes import views

# Les noms s'utilisent avec le préfixe "equipes:", ex. {% url 'equipes:liste' %}
app_name = "equipes"

urlpatterns = [
    # Pages (GET)
    path("", views.liste, name="liste"),
    path("<int:equipe_id>/", views.detail, name="detail"),

    # Actions (POST)
    path("creer/", views.creer, name="creer"),
    path("<int:equipe_id>/renommer/", views.renommer, name="renommer"),
    path("<int:equipe_id>/supprimer/", views.supprimer, name="supprimer"),
    path("<int:equipe_id>/ajouter/", views.ajouter, name="ajouter"),
    path("<int:equipe_id>/retirer/<int:numero>/", views.retirer, name="retirer"),
]
