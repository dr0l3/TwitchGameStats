#!/usr/bin/python3
import datetime
import redis
import functools
import os

#dbAddress = os.environ["DBADDRESS"]
POOL = redis.ConnectionPool(host="localhost", port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)


def add_two_numbers(a, b):
    return a + b



# compute average of last hour and add to average_every_hour db
current_date = int(datetime.datetime.now().timestamp())
oldest_possible_timestamp = current_date - (60 * 60)
list_of_game_names = db.smembers("gamelist")
for game in list_of_game_names:
    game = game.decode("utf-8")
    game_set_name = game + "-last_hour"
    db.zremrangebyscore(game_set_name, "-inf", oldest_possible_timestamp)
    list_of_events = db.zrange(game_set_name, 0, -1)
    if len(list_of_events) > 0:
        list_of_events = [int(float(x)) for x in list_of_events]
        average = sum(list_of_events) // len(list_of_events)
        if db.zadd(game + "-average_every_hour", current_date, average) == 0:
            db.zadd(game + "-average_every_hour", current_date, (repr(average) + "." + repr(current_date)))

print("Hourly updates done. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))