from .json_loader import load_json, save_json


fragments_state = {}
fragments_order = []  # pour chaque sous-titreur : liste ordonnée de ses fragments


def initialize_fragments():
    global fragments_state, fragments_order

    fragments = load_json("data/fragments.json", default=[])
    sous_titreurs = load_json("data/sous_titreurs.json", default={})

    # Répartition round-robin pour déterminer l'ordre
    connected = [k for k, v in sous_titreurs.items() if v == "connecté"]
    if not connected:
        print("[WARN] Aucun sous-titreur connecté")
        return

    fragments_state = {}
    fragments_order = {st: [] for st in connected}

    for i, frag in enumerate(fragments):
        st = connected[i % len(connected)]
        frag_id = frag["id"]
        fragments_state[frag_id] = {
            "start": frag["start"],
            "end": frag["end"],
            "sous_titreur": st,
            "done": False
        }
        fragments_order[st].append(frag_id)

    save_json("data/fragments_state.json", fragments_state)


def get_next_fragment(sous_titreur):
    """Retourne le prochain fragment non terminé du sous-titreur."""
    for frag_id in fragments_order.get(sous_titreur, []):
        info = fragments_state.get(frag_id)
        if info and not info["done"]:
            return frag_id, info
    return None, None


def mark_fragment_done(frag_id):
    """Marque un fragment comme terminé."""
    if frag_id in fragments_state:
        fragments_state[frag_id]["done"] = True
        save_json("data/fragments_state.json", fragments_state)
