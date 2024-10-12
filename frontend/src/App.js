import React, { useEffect, useState } from "react";

function WebSocketComponent() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [channels, setChannels] = useState([]);
  const [currentChannel, setCurrentChannel] = useState("");
  const [ws, setWs] = useState(null);

  // Fetch available channels
  useEffect(() => {
    fetch("http://localhost:8000/channels/")
      .then((response) => response.json())
      .then((data) => {
        setChannels(data.channels);
        setCurrentChannel(data.channels[0]);
      });

    // Request notification permission
    if (Notification.permission !== "granted") {
      Notification.requestPermission();
    }
  }, []);

  // Subscribe to a new channel
  const subscribeToChannel = (channel) => {
    if (ws) {
      ws.close();
    }
    const socket = new WebSocket(`ws://localhost:8000/ws/${channel}`);
    socket.onmessage = (event) => {
      setMessages((prev) => [...prev, event.data]);

      // Trigger push notification
      if (Notification.permission === "granted") {
        new Notification(`New message in ${channel}`, {
          body: event.data,
        });
      }
    };
    setWs(socket);
    setCurrentChannel(channel);
  };

  // Send message through WebSocket
  const sendMessage = (e) => {
    e.preventDefault();
    if (ws) {
      ws.send(message);
      setMessage("");
    }
  };

  return (
    <div>
      <h1>WebSocket Channel Subscription</h1>
      <div>
        <label>Select a channel to join:</label>
        <select
          value={currentChannel}
          onChange={(e) => subscribeToChannel(e.target.value)}
        >
          {channels.map((channel) => (
            <option key={channel} value={channel}>
              {channel}
            </option>
          ))}
        </select>
      </div>

      <form onSubmit={sendMessage}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button type="submit">Send</button>
      </form>

      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
    </div>
  );
}

export default WebSocketComponent;
