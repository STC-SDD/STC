from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.websocket_manager import WebSocketManager
from services import fragment_assigner

router = APIRouter()
ws_manager = WebSocketManager()


async def send_fragment(ws, sous_titreur):
    """Envoie 1 seul fragment (le prochain) à ce sous-titreur."""
    frag_id, info = fragment_assigner.get_next_fragment(sous_titreur)

    if frag_id is None:
        await ws.send_text("FIN")
        print(f"[INFO] Plus de fragments pour {sous_titreur}")
        return False

    msg = f"FRAG {frag_id} {info['start']} {info['end']}"
    await ws.send_text(msg)
    print(f"[DEBUG] Envoyé à {sous_titreur} : {msg}")

    return True


@router.websocket("/ws/{client}")
async def websocket_endpoint(ws: WebSocket, client: str):
    await ws_manager.connect(client, ws)

    # envoyer le premier fragment
    await send_fragment(ws, client)

    try:
        while True:
            data = await ws.receive_text()
            print(f"{client} a envoyé : {data}")

            # data = texte du sous-titre → marquer le fragment en cours comme terminé
            frag_id, info = fragment_assigner.get_next_fragment(client)
            
            # On peut recevoir un message du type "DONE frag3"
            if data.startswith("DONE"):
                _, frag_id = data.split()
                fragment_assigner.mark_fragment_done(frag_id)

                # puis envoyer le prochain fragment
                await send_fragment(ws, client)

    except WebSocketDisconnect:
        ws_manager.disconnect(client)
        print(f"{client} déconnecté")
