Projet de Sous-Titrage – Version 1
1. Description 

Cette application permet de gérer le sous-titrage de vidéos avec trois types d’utilisateurs :

Administrateur : Upload de vidéos, fragmentation et attribution des fragments aux sous-titreurs.

Sous-titreur : Reçoit les fragments assignés, écrit les sous-titres pour chaque fragment.

Watcher : Watch la video avec les sous-titres .

L’application est développée en Python (FastAPI) avec des pages front-end simples en HTML/CSS/JS.
Les données sont stockées dans des fichiers JSON (users.json, fragments.json, fragments_state.json, sous_titreurs.json) au lieu d’une base de données pour cette version.

2. Architecture du projet
version0.1/
├── main.py                  # Point d'entrée de l'application
├── data/
│   ├── fragments.json       # Fragments initiaux
│   ├── fragments_state.json # État actuel des fragments (assignation et statut)
│   └── sous_titreurs.json   # Liste des sous-titreurs et leur statut
├── static/
│   └── subtitler.html       # Interface front-end pour le sous-titreur
├── services/
│   ├── json_loader.py       # Fonctions pour lire et écrire dans les JSON
│   ├── fragment_assigner.py # Attribution des fragments aux sous-titreurs
│   └── websocket_manager.py # Gestion des WebSockets
└── models/
│   ├── user.py              # Modèle Pydantic pour les utilisateurs
│   ├── fragment.py          # Modèle Pydantic pour les fragments
│   └── subtitle.py          # Modèle Pydantic pour les sous-titres
├── video/
│   ├── sous_titrage.mp4     # Vidéo pour sous-titrage

3. Fonctionnement général

Connexion des sous-titreurs via la page / (front-end HTML).

Initialisation au démarrage :

Les fragments sont chargés depuis fragments.json.

Les sous-titreurs connectés sont listés dans sous_titreurs.json.

Les fragments sont attribués aux sous-titreurs en Round Robin.

L’état des fragments est sauvegardé dans fragments_state.json.

Sous-titreur :

Reçoit uniquement les fragments qui lui sont assignés via WebSocket.

Saisie des sous-titres pour chaque fragment.

Soumission des sous-titres au serveur.

WebSocket :

Permet de communiquer en temps réel avec chaque sous-titreur pour l’attribution des fragments et la réception des sous-titres.

Fusion :

Les sous-titres vont être fusionnés dans l’ordre des fragments pour générer le fichier final.

4. Lancer l’application
Prérequis
Python 3.10+
Packages Python : fastapi, uvicorn

Installation

# Installer les dépendances
pip install fastapi uvicorn
Exécution
Depuis le dossier contenant main.py :
uvicorn main:app --reload


L’application sera disponible à : http://127.0.0.1:8000/

Les sous-titreurs peuvent ouvrir la page dans leur navigateur et entrer leur nom pour se connecter.

5. Structure des fichiers JSON
sous_titreurs.json
{
    "Alice": "connecté",
    "Bob": "connecté"
}

fragments.json
[
    {"id": "frag1", "start": 0, "end": 5},
    {"id": "frag2", "start": 5, "end": 10}
]

fragments_state.json (généré automatiquement)
{
    "frag1": {"start": 0, "end": 5, "sous_titreur": "Alice", "statut": "en cours"},
    "frag2": {"start": 5, "end": 10, "sous_titreur": "Bob", "statut": "en cours"}
}