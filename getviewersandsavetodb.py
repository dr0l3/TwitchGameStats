#!/usr/bin/python3
import urllib.request
import urllib.parse
import json
import datetime
import redis
import os

dbAddress = os.environ['DBADDRESS']
POOL = redis.ConnectionPool(host=dbAddress, port=6379, db=0)
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
    db.sadd("gamelist", gamename)
    # append to the list
    if db.zadd(gamename + "-last_hour", timestamp, viewnumber) == 0:
        db.zadd(gamename + "-last_hour", timestamp, (repr(viewnumber) + "." + repr(timestamp)))


queryAddress = 'https://api.twitch.tv/kraken/games/top?limit=100'

response = urllib.request.urlopen(queryAddress)
html = response.read()

htmlAsJson = json.loads(html.decode("utf-8"))

top = htmlAsJson["top"]

current_top_10 = db.smembers("top_10_now")
current_top_10 = {x.decode("utf-8") for x in current_top_10}
new_top_10 = []
for i in range(10):
    top_10_game = top[i]
    new_top_10.append(top_10_game["game"]["name"])

difference = list(set(new_top_10) - set(current_top_10))
to_add = set(difference).intersection(new_top_10)
to_remove = set(difference).intersection(current_top_10)

for game in to_add:
    db.sadd("top_10_now", game)
for game in to_remove:
    db.srem("top_10_now", game)

for chans in top:
    game = chans["game"]["name"]
    viewers = chans["viewers"]
    date = datetime.datetime.now()
    addmeasurementtodb(game, viewers, int(date.timestamp()))

print("Viewership numbers downloaded. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
