from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import WebSocketManager
from services.fragment_assigner import (
    assign_next_fragment,
    mark_fragment_done,
    reassign_fragments_for_disconnected,
    add_user_to_roundrobin
)
from services.json_loader import load_json

router = APIRouter()
ws_manager = WebSocketManager()


@router.websocket("/ws/{username}")
async def ws_sub(ws: WebSocket, username: str):
    await ws_manager.connect(username, ws)
    add_user_to_roundrobin(username)

    # 1) Première attribution Round Robin
    frag = assign_next_fragment()
    if frag:
        await ws_manager.send_personal_message(
            username,
            f"FRAGMENT {frag['id']} {frag['start']} {frag['end']}"
        )
    else:
        await ws_manager.send_personal_message(username, "NO_FRAGMENT_AVAILABLE")

    try:
        while True:
            text = await ws.receive_text()

            # Nouveau fragment VAD disponible
            if text == "REQUEST_FRAGMENT":
                next_frag = assign_next_fragment()
                if next_frag:
                    await ws_manager.send_personal_message(
                        username,
                        f"FRAGMENT {next_frag['id']} {next_frag['start']} {next_frag['end']}"
                    )
                else:
                    await ws_manager.send_personal_message(username, "NO_FRAGMENT_AVAILABLE")
                continue

            # Soumission de sous-titre
            state = load_json("data/fragments_state.json", default={})

            current = None
            for fid, info in state.items():
                if info["sous_titreur"] == username and info["statut"] == "en cours":
                    current = fid
                    break

            if not current:
                continue

            # Marquer fini
            mark_fragment_done(current, text)
            await ws_manager.send_personal_message(username, f"ACK {current}")

            # Nouveau fragment Round Robin
            next_frag = assign_next_fragment()
            if next_frag:
                await ws_manager.send_personal_message(
                    username,
                    f"FRAGMENT {next_frag['id']} {next_frag['start']} {next_frag['end']}"
                )
            else:
                await ws_manager.send_personal_message(username, "NO_MORE_FRAGMENTS")

    except WebSocketDisconnect:
        ws_manager.disconnect(username)
        reassign_fragments_for_disconnected(username)
