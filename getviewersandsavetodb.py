#!/usr/bin/python3
import urllib.request
import urllib.parse
import json
import datetime
import redis
import os

# dbAddress = os.environ["dbAddress"]
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)


# def addmeasurement(name, viewernumber, date):
#    if games.__contains__(name):
#        item = games[name]
#    else:
#        games[name] = []
#        item = games[name]
#    tupleOfMeasurement = (viewernumber, date)
#    item.append(tupleOfMeasurement)


def addmeasurementtodb(gamename, viewnumber, timestamp):
    # get the listname from the name
    setname = "".join(gamename.split())
    db.sadd("gamelist", gamename)
    # append to the list
    if db.zadd(gamename+"-last_hour", timestamp, viewnumber) == 0:
        db.zadd(gamename+"-last_hour", timestamp, (repr(viewnumber) + "." + repr(timestamp)))


queryAddress = 'https://api.twitch.tv/kraken/games/top?limit=100'

response = urllib.request.urlopen(queryAddress)
html = response.read()

htmlAsJson = json.loads(html.decode("utf-8"))

top = htmlAsJson["top"]

for chans in top:
    game = chans["game"]["name"]
    viewers = chans["viewers"]
    date = datetime.datetime.now()
    addmeasurementtodb(game, viewers, int(date.timestamp()))

print("Done. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
