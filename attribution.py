# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 09:54:13 2025

@author: marie
"""

import csv

# Exemple de données
fragments = [
    {"id": 1, "start": 0.0, "end": 3.5},
    {"id": 2, "start": 3.5, "end": 7.0},
    {"id": 3, "start": 7.0, "end": 10.5},
    {"id": 4, "start": 10.5, "end": 15.0},
]

sous_titreurs = ["Alice", "Bob", "Charlie"]

# Round Robin : attribution
attributions = {}
for i, fragment in enumerate(fragments):
    sous_titreur = sous_titreurs[i % len(sous_titreurs)]
    attributions[fragment["id"]] = sous_titreur

# Affichage
for fragment_id, st in attributions.items():
    print(f"Fragment {fragment_id} → {st}")

# Enregistrement dans un fichier CSV
with open("attributions.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["FragmentID", "Sous-titreur"])
    for fragment_id, st in attributions.items():
        writer.writerow([fragment_id, st])
