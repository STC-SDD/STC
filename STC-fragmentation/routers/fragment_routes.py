from fastapi import APIRouter
from services.json_loader import load_json, save_json

router = APIRouter()

@router.get("/my_fragments/{username}")
def get_user_fragments(username: str):
    state = load_json("data/fragments_state.json")

    user_frags = [
        {"id": fid, **info}
        for fid, info in state.items()
        if info["sous_titreur"].lower() == username.lower()
    ]

    return user_frags


@router.post("/submit_fragment/{fragment_id}")
def submit_fragment(fragment_id: int, text: str):
    state = load_json("data/fragments_state.json")

    if str(fragment_id) not in state:
        return {"error": "fragment introuvable"}

    # Marquer le fragment comme terminé
    state[str(fragment_id)]["statut"] = "terminé"

    # Sauvegarder le texte envoyé
    subtitles = load_json("data/subtitles.json")
    subtitles.append({
        "start": state[str(fragment_id)]["start"],
        "end": state[str(fragment_id)]["end"],
        "text": text
    })

    save_json("data/subtitles.json", subtitles)
    save_json("data/fragments_state.json", state)

    return {"message": "fragment envoyé et sauvegardé"}
