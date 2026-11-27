# Préparation des données pour l'affichage (partie interface, personne B)

STAT_LABELS = {
    "hp": "PV",
    "attack": "Attaque",
    "defense": "Défense",
    "special-attack": "Att. spé.",
    "special-defense": "Déf. spé.",
    "speed": "Vitesse",
}


def noms(elements, cle):
    """Renvoie une liste de noms, que les données soient
    ["electric"] ou [{"type": {"name": "electric"}}]."""
    resultat = []
    for e in elements:
        if isinstance(e, str):
            resultat.append(e)
        else:
            resultat.append(e[cle]["name"])
    return resultat


def preparer_stats(stats):
    resultat = []
    for s in stats:
        valeur = s["base_stat"]
        nom = s["stat"]["name"]
        if valeur < 60:
            niveau = "bas"
        elif valeur < 90:
            niveau = "moyen"
        else:
            niveau = "haut"
        resultat.append({
            "label": STAT_LABELS.get(nom, nom),
            "valeur": valeur,
            "pourcent": round(valeur / 255 * 100),
            "niveau": niveau,
        })
    return resultat