class WebSocketManager:
    def __init__(self):
        self.clients = {}

    async def connect(self, name, ws):
        await ws.accept()
        self.clients[name] = ws

    def disconnect(self, name):
        if name in self.clients:
            del self.clients[name]

    async def send_personal_message(self, name, message):
        ws = self.clients.get(name)
        if ws:
            await ws.send_text(message)
