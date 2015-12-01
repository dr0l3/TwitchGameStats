import urllib.request
import urllib.parse
import json
import datetime
import pickle


with open("GameHistory", "rb") as f:
    games = pickle.load(f)


def addmeasurement(name, viewernumber, date):
    if games.__contains__(name):
        item = games[name]
    else:
        games[name] = []
        item = games[name]
    tupleOfMeasurement = (viewernumber, date)
    item.append(tupleOfMeasurement)


queryAddress = 'http://api.twitch.tv/kraken/games/top?limit=50'

response = urllib.request.urlopen(queryAddress)
html = response.read()

htmlAsJson = json.loads(html.decode("latin-1"))

top = htmlAsJson["top"]

for chans in top:
    game = chans["game"]["name"]
    viewers = chans["viewers"]
    date = datetime.datetime.now()
    addmeasurement(game, viewers, date)

with open("GameHistory", "wb") as f:
    pickle.dump(games, f)

print("Done")
