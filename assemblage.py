# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 14:16:12 2025

@author: marie
"""

import csv

# fragments fictifs
fragments = [
    {"id": 1, "start": 0.0, "end": 3.5},
    {"id": 2, "start": 3.5, "end": 7.0},
    {"id": 3, "start": 7.0, "end": 10.5},
    {"id": 4, "start": 10.5, "end": 15.0},
]

sous_titreurs = ["Alice", "Bob", "Charlie"]

#Round Robin
fragments_state = {}
for i, fragment in enumerate(fragments):
    sous_titreur = sous_titreurs[i % len(sous_titreurs)]
    fragments_state[fragment["id"]] = {"sous_titreur": sous_titreur, "statut": "en cours"}

#État des sous-titreurs 
sous_titreur_statuts = {
    "Alice": "connecté",
    "Bob": "connecté",
    "Charlie": "déconnecté"
}

# Gestion dynamique: réattribuer si déconnexion ou fragment non traité
for frag_id, info in fragments_state.items():
    if (info['sous_titreur'] == "Charlie" and sous_titreur_statuts["Charlie"] != "connecté"
        and info['statut'] != "terminé"):
        fragments_state[frag_id]['sous_titreur'] = None
        fragments_state[frag_id]['statut'] = "à réattribuer"

for frag_id, info in fragments_state.items():
    if info['statut'] == "à réattribuer":
        for st in sous_titreurs:
            if sous_titreur_statuts[st] == "connecté":
                fragments_state[frag_id]['sous_titreur'] = st
                fragments_state[frag_id]['statut'] = "en cours"
                break


print("Simulation attribution dynamique après déconnexion :")
for frag_id, info in fragments_state.items():
    print(f"Fragment {frag_id} → {info['sous_titreur']}, statut : {info['statut']}")

# Enregistrement dans un CSV pour vérification ou archivage
with open("attributions_finales.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["FragmentID", "Sous-titreur", "Statut"])
    for frag_id, info in fragments_state.items():
        writer.writerow([frag_id, info['sous_titreur'], info['statut']])
