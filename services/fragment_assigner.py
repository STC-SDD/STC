from .json_loader import load_json, save_json

fragments_state = {}

def attribuer_fragments(fragments, sous_titreurs):
    state = {}
    connected = [k for k, v in sous_titreurs.items() if v == "connecté"]

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
    # Charger les fragments, créer un fichier vide s'il n'existe pas ou s'il est invalide
    fragments = load_json("data/fragments.json", default=[])
    if fragments == []:
        save_json("data/fragments.json", fragments)

    # Adapter les formats éventuels {"segments": [...]} en liste de fragments attendus
    if isinstance(fragments, dict) and "segments" in fragments:
        segs = fragments["segments"] or []
        # Générer des IDs stables via index
        fragments = [
            {
                "id": f"seg_{i+1:03d}",
                "start": s.get("start_time", s.get("start")),
                "end": s.get("end_time", s.get("end"))
            }
            for i, s in enumerate(segs)
            if s is not None
        ]
        save_json("data/fragments.json", fragments)

    sous_titreurs = load_json("data/sous_titreurs.json", default={})
    fragments_state = attribuer_fragments(fragments, sous_titreurs)
