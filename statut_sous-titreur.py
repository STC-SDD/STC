# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 13:24:55 2025

@author: marie
"""

sous_titreurs = ['Alice', 'Bob', 'Charlie']

sous_titreur_statuts = {
    "Alice": "connecté",
    "Bob": "connecté",
    "Charlie": "déconnecté"
}

#s’il est en cours, attribué, terminé ou “à réattribuer”.
fragments_state = {
    1: {"sous_titreur": "Alice", "statut": "terminé"},
    2: {"sous_titreur": "Bob", "statut": "en cours"},
    3: {"sous_titreur": "Charlie", "statut": "en cours"},
    4: {"sous_titreur": None, "statut": "à attribuer"}
}


#Si un sous-titreur se déconnecte/inactif
for frag_id, info in fragments_state.items():
    if (info['sous_titreur'] == "Charlie" and sous_titreur_statuts["Charlie"] != "connecté"
        and info['statut'] != "terminé"):
        fragments_state[frag_id]['sous_titreur'] = None
        fragments_state[frag_id]['statut'] = "à réattribuer"

#Réattribution dans la boucle principale
for frag_id, info in fragments_state.items():
    if info['statut'] == "à réattribuer":
        for st in sous_titreurs:
            if sous_titreur_statuts[st] == "connecté":
                fragments_state[frag_id]['sous_titreur'] = st
                fragments_state[frag_id]['statut'] = "en cours"
                break

for frag_id, info in fragments_state.items():
    print(f"Fragment {frag_id} ⇒ {info['sous_titreur']}, statut : {info['statut']}")
