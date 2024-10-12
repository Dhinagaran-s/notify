from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory data structures for managing channels and subscriptions
channels = ["general", "sports", "news", "tech"]  # Available channels
subscriptions: Dict[str, List[WebSocket]] = {
    channel: [] for channel in channels
}  # Track channel subscriptions


class Message(BaseModel):
    message: str


class ChannelMessage(Message):
    message: str
    channel: str  # Add channel to broadcast messages to specific channels


# WebSocket Manager to handle multiple connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def subscribe(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        subscriptions[channel].append(websocket)

    def unsubscribe(self, websocket: WebSocket, channel: str):
        subscriptions[channel].remove(websocket)

    async def channel_broadcast(self, message: str, channel: str):
        if channel not in subscriptions:
            raise HTTPException(status_code=404, detail="Channel not found")
        for connection in subscriptions[channel]:
            await connection.send_text(message)


manager = ConnectionManager()


# List available channels
@app.get("/channels/")
async def list_channels():
    return {"channels": channels}


# WebSocket route for clients to connect to a specific channel
@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    if channel not in channels:
        await websocket.close()
        return
    await manager.subscribe(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.channel_broadcast(f"{channel}: {data}", channel)
    except WebSocketDisconnect:
        manager.unsubscribe(websocket, channel)



# WebSocket route for clients to connect to a specific client
@app.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Sending message to all connected clients
            await manager.broadcast(f"Client {user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)






# HTTP route to trigger WebSocket broadcast for a channel
@app.post("/send-message/")
async def send_message(msg: ChannelMessage):
    if msg.channel not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    # Broadcast message to the WebSocket clients in the channel
    await manager.channel_broadcast(
        f"Broadcast to {msg.channel}: {msg.message}", msg.channel
    )
    return {"message": f"Message sent to {msg.channel}"}


# HTTP route to trigger WebSocket broadcast
@app.post("/users/send-message/")
async def send_message(message: str):
    await manager.broadcast(f"Broadcast: {message}")
    return {"message": "Message sent to all clients"}




# HTML for testing via browser
@app.get("/")
async def get():
    html_content = """
    <html>
        <head>
            <title>WebSocket Channel Subscription</title>
        </head>
        <body>
            <h1>WebSocket Channel Subscription</h1>

            <div>
                <label>Select a channel to join:</label>
                <select id="channels"></select>
                <button onclick="subscribe()">Subscribe</button>
            </div>

            <form id="form">
                <input type="text" id="messageInput" autocomplete="off"/>
                <button type="submit">Send</button>
            </form>

            <ul id="messages"></ul>

            <script>
                let ws;
                let currentChannel = '';

                // Fetch available channels from the server
                fetch("http://localhost:8000/channels/")
                    .then(response => response.json())
                    .then(data => {
                        const channelSelect = document.getElementById('channels');
                        data.channels.forEach(channel => {
                            const option = document.createElement('option');
                            option.value = channel;
                            option.text = channel;
                            channelSelect.appendChild(option);
                        });
                    });

                // Subscribe to a channel
                function subscribe() {
                    const channel = document.getElementById('channels').value;

                    // Close the existing WebSocket connection if any
                    if (ws) ws.close();

                    // Create a new WebSocket connection for the selected channel
                    ws = new WebSocket(`ws://localhost:8000/ws/${channel}`);
                    currentChannel = channel;

                    ws.onmessage = function(event) {
                        // Display the received message in the message list
                        const messages = document.getElementById('messages');
                        const message = document.createElement('li');
                        message.textContent = event.data;
                        messages.appendChild(message);

                        // Trigger browser push notification
                        if (Notification.permission === "granted") {
                            new Notification(`New message in ${channel}`, {
                                body: event.data,
                            });
                        }
                    };
                }

                // Handle form submission to send a message
                document.getElementById('form').onsubmit = function(event) {
                    event.preventDefault();
                    const input = document.getElementById("messageInput");

                    if (ws) {
                        ws.send(input.value);  // Send the message via WebSocket
                        input.value = '';  // Clear the input field
                    }
                };

                // Request notification permission on page load
                if (Notification.permission !== "granted") {
                    Notification.requestPermission().then(permission => {
                        if (permission === "granted") {
                            console.log("Notification permission granted.");
                        } else {
                            console.log("Notification permission denied.");
                        }
                    });
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
