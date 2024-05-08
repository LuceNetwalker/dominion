from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import json
import eventlet

from dominion import make_premade_game, make_random_game, WebsocketPlayer
import dominion.cards
import dominion_ai


app = Flask(__name__)
# socketio = SocketIO(app, async_mode="threading")
socketio = SocketIO(app, async_mode="eventlet")

@socketio.on('connect')
def handle_connect():
    print('Websocket connected')



@socketio.on('user_join')
def play_game(args):

    print('Starting game with {}'.format(args))

    player = WebsocketPlayer(args['name'], socketio)  # Use sid to identify the client
    ai = getattr(dominion_ai, args['ai'])(args['ai'])

    if args['game'] == 'random':
        reqs = set(map(lambda req: getattr(dominion.cards, req), args['requires']))
        reqs.update(ai.requires())
        game = make_random_game(player, ai, reqs)
    else:
        game = make_premade_game(player, ai, args['game'])

    game.start()
    while not game.is_over():
        game.run_next_phase()
    game.complete()

    print('Finished game.')

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000)
