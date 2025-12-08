from .json_loader import load_json, save_json

# Variable globale maintenue à jour
fragments_state = {}


def attribuer_fragments(fragments, sous_titreurs):
    state = {}
    connected = [k for k, v in sous_titreurs.items() if v == "connecté"]

    if not connected:
        print("[WARN] Aucun sous-titreur connecté → aucune attribution possible.")
        return {}

    for i, frag in enumerate(fragments):
        st = connected[i % len(connected)]
        state[frag["id"]] = {
            "start": frag["start"],
            "end": frag["end"],
            "sous_titreur": st,
            "statut": "en cours"
        }

    save_json("data/fragments_state.json", state)
    return state


def initialize_fragments():
    global fragments_state

    # Charger les fragments
    fragments = load_json("data/fragments.json", default=[])

    # Convertir format {"segments": [...]} → liste simple
    if isinstance(fragments, dict) and "segments" in fragments:
        segs = fragments["segments"] or []
        fragments = [
            {
                "id": f"seg_{i+1:03d}",
                "start": s.get("start_time", s.get("start")),
                "end": s.get("end_time", s.get("end"))
            }
            for i, s in enumerate(segs)
            if s
        ]
        save_json("data/fragments.json", fragments)

    # Charger les sous-titreurs
    sous_titreurs = load_json("data/sous_titreurs.json", default={})

    # Mettre à jour la variable globale
    fragments_state = attribuer_fragments(fragments, sous_titreurs)
    print("[INFO] fragments_state initialisé :", fragments_state)
