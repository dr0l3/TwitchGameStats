import redis
import datetime

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)

# get list of all games
listofgames = db.hvals("shorttermgamelist")
# print(listofgames)
# for each game in list
for game in listofgames:
    # get list of viewers and timestamps
    listoftuples = db.lrange(game, 0, -1)
    # for each tuple
    total = 0
    for tuplestring in listoftuples:
        viewers, timestamp = eval(tuplestring)
        # sum
        total += viewers
    # calculate average
    average = total / len(listoftuples)
    # print average
    print(repr(game) + " = " + repr(average))

print("Done")
