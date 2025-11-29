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
    fragments = load_json("data/fragments.json")
    sous_titreurs = load_json("data/sous_titreurs.json")
    fragments_state = attribuer_fragments(fragments, sous_titreurs)
