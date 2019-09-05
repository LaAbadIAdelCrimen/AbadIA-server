from typing import List, Any

from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
import requests

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)

# AbadIA

loadedGame    = {}
loadedActions = {}


def createRejilla(step):
    reji = []
    floorLevel = step['Personajes'][0]['altura']
    rejilla = step['Rejilla']

    for y in range(0, 24):
        row = []
        for x in range(0, 24):
            alt = rejilla[y][x] % 16 - floorLevel
            zone = int(rejilla[y][x] / 16)

            who = -1
            ori = -1
            if zone > 0:
                who = -1 + (-zone)
            for per in step['Personajes']:
                tmpX = per['posX'] % 16 + 4
                tmpY = per['posY'] % 16 + 3
                if (tmpX == x and tmpY == y):
                    print("personaje {} en {},{}".format(per['id'], tmpX, tmpY))
                    who = per['id']
                    ori = per['orientacion']
            vals = [who, ori, alt]
            row.append(vals)
        reji.append(row)

    step['rejilla'] = reji


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


# list of files

@app.route('/list', methods=['GET'])
def list_of_files():
    res = requests.get('https://storage.googleapis.com/abadia-data/last_20000abadia_actions_list.txt')
    return res.text # jsonify('pong!')





@app.route('/game', methods=['GET'])
def game():
    # filename = os.path.join("/tmp", "game.json"),
    global loadedActions
    global loadedGame

    loadedActions = {}

    with open("game.json") as gameFile:
            for cnt, line in enumerate(gameFile):
                # print("Line {}: {}".format(cnt, line))
                loadedActions.update({str(cnt): json.loads(line)[0]})
    # loadedActions = actions
    loadedGame.update({'filename': 'game.json', 'actions': len(loadedActions)})

    # abadia_actions_180608_235540_290496.json
    return jsonify({
        'status': 'success',
        'game': loadedGame
    })

@app.route('/action/<index>', methods=['GET'])
def action(index):
    global loadedActions
    global loadedGame

    print("index ({})".format(index))
    print("game ({})".format(loadedGame))
    print("actions ({})".format(loadedActions[index]))
    # print("action {}".format(loadedActions[int(index)]))

    if int(index) > len(loadedActions) or len(loadedActions) == 0:
        step = {'action': {}}
    else:
        step = loadedActions[index]

    if int(index)+1 == len(loadedActions):
        next = index
    else:
        next = str(int(index)+1)

    if int(index)-1 < 0:
        prev = '0'
    else:
        prev = str(int(index)-1)

    createRejilla(step['action']['state'])
    createRejilla(step['action']['nextstate'])

    return jsonify({
        'status': 'success',
        'game': loadedGame,
        'next': next,
        'prev': prev,
        'action': step['action']

    })


if __name__ == '__main__':
    app.run()
