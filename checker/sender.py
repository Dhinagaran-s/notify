from requests import post
from requests.exceptions import ConnectionError
# Sending a message to the FastAPI broadcast endpoint
try:
    response = post(
        "http://localhost:8000/send-message/",
        json={"channel": "tech", "message": "Hello WebSocket clients!"},
    )
    print(response.json())  # Output: {"message": "Message sent to all clients"}
except ConnectionError:
    print("Unable to connect to endpoint, kindly check is the endpoint is live")
