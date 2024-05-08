from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from flask import Flask
from flask_sock import Sock

app = Flask(__name__)
sockets = Sock(app)

@sockets.route('/echo')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        if message is not None:
            ws.send(message)

@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()