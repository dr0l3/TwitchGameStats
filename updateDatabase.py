#!/usr/bin/python3
import urllib.request
import urllib.parse
import json
import datetime
import redis
import functools
import os

# dbAddress = os.environ["dbAddress"]
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)


def add_two_numbers(a, b):
    return a + b


def addmeasurementtodb(gamename, viewnumber, timestamp):
    # get the listname from the name
    setname = "".join(gamename.split())
    # append to the list
    if db.zadd(gamename, timestamp, viewnumber) == 0:
        db.zadd(gamename, timestamp, (repr(viewnumber) + "." + repr(timestamp)))


# compute average of last hour and add to average_every_hour db
current_date = int(datetime.datetime.now().timestamp())
list_of_game_names = db.smembers("gamelist")
for game in list_of_game_names:
    game = game.decode("utf-8")
    game_set_name = game + "-last_hour"

    oldest_possible_timestamp = current_date + 60 * 60
    db.zremrangebyscore(game_set_name, oldest_possible_timestamp, '+inf')
    list_of_events = db.zrange(game_set_name, 0, -1)
    average = functools.reduce(add_two_numbers, [int(float(x)) for x in list_of_events]) // len(list_of_events)
    if db.zadd(game + "-average_every_hour", current_date, average) == 0:
        db.zadd(game + "-average_every_hour", current_date, (repr(average) + "." + repr(current_date)))

for game in list_of_game_names:
    game = game.decode("utf-8")
    game_set_name = game + "-average_every_hour"

    oldest_possible_timestamp = current_date + 60 * 60 * 24 * 30
    list_of_too_old_stuff = db.zrangebyscore(game_set_name, oldest_possible_timestamp, "+inf")
    db.zremrangebyscore(game_set_name, oldest_possible_timestamp, "+inf")
    if len(list_of_too_old_stuff) > 0:
        average = functools.reduce(add_two_numbers, [int(float(x)) for x in list_of_too_old_stuff]) // len(
            list_of_too_old_stuff)
    else:
        average = 0

    if db.zadd(game + "-average_every_day", current_date, average) == 0:
        db.zadd(game + "-average_every_day", current_date, (repr(average) + "." + repr(current_date)))

        # find list of stuff that is between 30 and 31 days old
        # average it
        # insert into db
