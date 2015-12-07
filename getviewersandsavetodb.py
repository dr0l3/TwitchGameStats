import urllib.request
import urllib.parse
import json
import datetime
import redis
import os

dbAddress = os.environ["dbAddress"]
POOL = redis.ConnectionPool(host=dbAddress, port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)


#def addmeasurement(name, viewernumber, date):
#    if games.__contains__(name):
#        item = games[name]
#    else:
#        games[name] = []
#        item = games[name]
#    tupleOfMeasurement = (viewernumber, date)
#    item.append(tupleOfMeasurement)


def addmeasurementtodb(name, viewnumber, date):
    #get the listname from the name
    listname = db.hget("shorttermgamelist", name)
    if listname is None:
        namestripped = "".join(name.split())
        db.hset("shorttermgamelist", name, namestripped)
        listname = namestripped
    #append to the list
    db.lpush(listname, (viewnumber, date))

queryAddress = 'http://api.twitch.tv/kraken/games/top?limit=50'

response = urllib.request.urlopen(queryAddress)
html = response.read()

htmlAsJson = json.loads(html.decode("latin-1"))

top = htmlAsJson["top"]

for chans in top:
    game = chans["game"]["name"]
    viewers = chans["viewers"]
    date = datetime.datetime.now()
    addmeasurementtodb(game, viewers, date)

print("Done")
