# services/fragment_assigner.py
import os
from .json_loader import load_json, save_json

FRAGMENTS_FILE = "data/fragments.json"
STATE_FILE = "data/fragments_state.json"
RR_FILE = "data/roundrobin.json"
SUBTITLES_FILE = "data/subtitles.json"


def initialize_fragments():
    print("[DEBUG init] initialize_fragments() called")
    if not os.path.exists(STATE_FILE):
        print("[DEBUG init] fragments_state.json not found, creating {}")
        save_json(STATE_FILE, {})
    else:
        state = load_json(STATE_FILE, default={})
        print("[DEBUG init] fragments_state.json exists, loaded state keys:", list(state.keys()))

    if not os.path.exists(RR_FILE):
        print("[DEBUG init] roundrobin.json not found, creating empty order")
        save_json(RR_FILE, {"order": [], "index": 0})
    else:
        rr = load_json(RR_FILE, default={"order": [], "index": 0})
        print("[DEBUG init] roundrobin.json exists, order:", rr.get("order"), "index:", rr.get("index"))


# -------------------------------
# ROUND ROBIN : gestion utilisateurs
# -------------------------------

def add_user_to_roundrobin(username: str):
    rr = load_json(RR_FILE, default={"order": [], "index": 0})
    print(f"[DEBUG RR] add_user_to_roundrobin({username}) | before:", rr)
    if username not in rr["order"]:
        rr["order"].append(username)
        save_json(RR_FILE, rr)
        print(f"[DEBUG RR] {username} ajouté au round robin | after:", rr)
    else:
        print(f"[DEBUG RR] {username} déjà dans le round robin")
    return rr


def remove_user_from_roundrobin(username: str):
    rr = load_json(RR_FILE, default={"order": [], "index": 0})
    print(f"[DEBUG RR] remove_user_from_roundrobin({username}) | before:", rr)
    if username in rr["order"]:
        rr["order"].remove(username)
        rr["index"] = rr["index"] % max(len(rr["order"]), 1)
        save_json(RR_FILE, rr)
        print(f"[DEBUG RR] {username} retiré du round robin | after:", rr)
    else:
        print(f"[DEBUG RR] {username} n'était pas dans le round robin")


# -------------------------------
# ROUND ROBIN : attribution
# -------------------------------

def get_next_user_roundrobin():
    rr = load_json(RR_FILE, default={"order": [], "index": 0})
    print("[DEBUG RR] get_next_user_roundrobin() | rr =", rr)

    if not rr["order"]:
        print("[DEBUG RR] aucun utilisateur dans le round robin")
        return None

    user = rr["order"][rr["index"]]
    rr["index"] = (rr["index"] + 1) % len(rr["order"])
    save_json(RR_FILE, rr)

    print(f"[DEBUG RR] next user = {user}, new index = {rr['index']}")
    return user


def assign_next_fragment(username=None):
    """
    Si username=None → attribution Round Robin
    Si username fourni → attribue à cet utilisateur
    """
    print(f"[DEBUG assign] assign_next_fragment(username={username}) called")

    fragments = load_json(FRAGMENTS_FILE, default=[])
    state = load_json(STATE_FILE, default={})

    print(f"[DEBUG assign] fragments.json contient {len(fragments)} fragments")
    print(f"[DEBUG assign] fragments_state.json a les ids:", list(state.keys()))

    assigned = set(state.keys())

    # Trouver le premier fragment non attribué
    for frag in fragments:
        fid = str(frag["id"])
        if fid not in assigned:
            print(f"[DEBUG assign] fragment libre trouvé: {fid}")

            # Round Robin => on ignore le username et on choisit dans la rotation
            if username is None:
                username = get_next_user_roundrobin()

            print(f"[DEBUG assign] utilisateur choisi pour {fid} :", username)

            if not username:
                print("[DEBUG assign] aucun utilisateur dispo dans le round robin → return None")
                return None

            state[fid] = {
                "start": frag["start"],
                "end": frag["end"],
                "sous_titreur": username,
                "statut": "en cours"
            }
            save_json(STATE_FILE, state)
            print(f"[DEBUG assign] fragment {fid} attribué à {username}")
            return {"id": fid, **state[fid]}

    print("[DEBUG assign] aucun fragment libre trouvé → return None")
    return None


# -------------------------------
# MARQUAGE / RÉASSIGNATION
# -------------------------------

def mark_fragment_done(fid: str, subtitle=None):
    print(f"[DEBUG done] mark_fragment_done(fid={fid}, subtitle={subtitle})")
    state = load_json(STATE_FILE, default={})
    fid = str(fid)

    if fid not in state:
        print(f"[DEBUG done] fragment {fid} introuvable dans state")
        return False

    st = state[fid]["sous_titreur"]
    state[fid]["statut"] = "done"
    save_json(STATE_FILE, state)
    print(f"[DEBUG done] fragment {fid} marqué done pour {st}")

    # stocker texte
    if subtitle:
        subs = load_json(SUBTITLES_FILE, default={})
        subs[fid] = {
            "text": subtitle,
            "sous_titreur": st,
            "start": state[fid]["start"],
            "end": state[fid]["end"]
        }
        save_json(SUBTITLES_FILE, subs)
        print(f"[DEBUG done] sous-titre sauvegardé pour {fid}")

    return True


def reassign_fragments_for_disconnected(username: str):
    """
    Retire ses fragments "en cours"
    """
    print(f"[DEBUG reassign] reassign_fragments_for_disconnected({username})")
    state = load_json(STATE_FILE, default={})
    modified = False

    for fid, info in list(state.items()):
        if info["sous_titreur"] == username and info["statut"] == "en cours":
            print(f"[DEBUG reassign] suppression de l'attribution sur {fid}")
            del state[fid]
            modified = True

    if modified:
        save_json(STATE_FILE, state)
        print("[DEBUG reassign] state mis à jour après suppression")

    remove_user_from_roundrobin(username)
