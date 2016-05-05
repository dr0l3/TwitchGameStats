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



def addmeasurementtodb(gamename, viewnumber, timestamp):
    db.sadd("gamelist", gamename)
    # append to the list
    if db.zadd(gamename + "-last_hour", timestamp, viewnumber) == 0:
        db.zadd(gamename + "-last_hour", timestamp, (repr(viewnumber) + "." + repr(timestamp)))


queryAddressTopGames = 'https://api.twitch.tv/kraken/games/top?limit=100'
responseTopGames = urllib.request.urlopen(queryAddressTopGames)
htmlTopGames = responseTopGames.read()
htmlAsJsonTopGames = json.loads(htmlTopGames.decode("utf-8"))
top = htmlAsJsonTopGames["top"]

queryAddressSummary = 'https://api.twitch.tv/kraken/streams/summary'
responseSummary = urllib.request.urlopen(queryAddressSummary)
htmlSummary = responseSummary.read()
htmlAsJsonSummary = json.loads(htmlSummary.decode("utf-8"))
total_viewers = htmlAsJsonSummary["viewers"]
db.set("total_current_viewers", total_viewers)

current_top_10 = db.smembers("top_10_now")
current_top_10 = {x.decode("utf-8") for x in current_top_10}
new_top_10 = []
for i in range(10):
    top_10_game = top[i]
    new_top_10.append(top_10_game["game"]["name"])
diff = set(new_top_10).symmetric_difference(set(current_top_10))
to_add = set(diff).intersection(new_top_10)
to_remove = set(diff).intersection(current_top_10)

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
