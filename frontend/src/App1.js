import React, { useEffect, useState } from "react";

function WebSocketComponent() {
  const [messages, setMessages] = useState([]);
  const [socket, setSocket] = useState(null);
  const [inputValue, setInputValue] = useState("");

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = new WebSocket("ws://localhost:8000/ws/123"); // Replace 123 with unique client ID
    setSocket(newSocket);

    // On receiving a message from the server
    newSocket.onmessage = (event) => {
      const newMessage = event.data;
      console.log("new message",newMessage);
      
      setMessages((prevMessages) => [...prevMessages, newMessage]);

      // Display a visual alert
      // alert("New Notification: " + newMessage);

      // Optionally, trigger browser notification
      if (Notification.permission === "granted") {
        new Notification("New Notification", { body: newMessage });
      }
    };

    newSocket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    // Cleanup when component unmounts
    return () => newSocket.close();
  }, []);

  const sendMessage = () => {
    if (socket) {
      socket.send(inputValue);
      setInputValue("");
    }
  };

  // Request notification permission from the user
  const requestNotificationPermission = () => {
    if (Notification.permission !== "granted") {
      Notification.requestPermission().then(permission => {
        if (permission === "granted") {
          alert("Notification permission granted");
        }
      });
    }
  };

  return (
    <div>
      <h1>WebSocket Push Notifications</h1>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Type a message"
      />
      <button onClick={sendMessage}>Send Message</button>

      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>

      {/* Button to request notification permission */}
      <button onClick={requestNotificationPermission}>Enable Browser Notifications</button>
    </div>
  );
}

export default WebSocketComponent;
