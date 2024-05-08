import websocket

def on_message(ws, message):
    print(f"Received message from server: {message}")

def on_error(ws, error):
    print(f"Error occurred: {error}")

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    # Send a message to the server
    ws.send("Hello from client")

if __name__ == "__main__":
    # WebSocket server URL
    ws_url = "ws://127.0.0.1:5000/echo"

    # Create WebSocket connection
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)


    # Start WebSocket connection
    ws.run_forever()