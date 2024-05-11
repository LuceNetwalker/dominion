from flask import Flask, render_template, request
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

userdict: list[WebsocketPlayer] = {}


@socketio.event
def user_join(data):
    for player in userdict.values():
        if data['name'] in player.name:
            socketio.emit('choose_other_name')
            eventlet.sleep()
            return
    
    player = WebsocketPlayer(data['name'], socketio)
    userdict[request.sid] = player
    return

@socketio.on('disconnect')
def handle_disconnect():
    userdict.pop(request.sid)

@socketio.on('start_game')
def play_game(args):

    print('Starting game with {}'.format(args))

    # player = WebsocketPlayer(args['name'], socketio)  # Use sid to identify the client
    ai = getattr(dominion_ai, 'BigMoneyPlayer')('BigMoneyPlayer')
    userdict['BigMoneyPlayer'] = ai

    if args['game'] == 'random':
        # reqs = set(map(lambda req: getattr(dominion.cards, req), args['requires']))
        reqs = set()
        reqs.update(ai.requires())
        game = make_random_game(userdict.values(), reqs)
    else:
        game = make_premade_game(userdict.values(), args['game'])

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
