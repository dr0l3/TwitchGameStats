#!/usr/bin/python3
import datetime
import redis
import functools
import os

dbAddress = os.environ["DBADDRESS"]
POOL = redis.ConnectionPool(host=dbAddress, port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)


def add_two_numbers(a, b):
    return a + b


# compute average of last date between 30 and 31 days old then remove it from hourly-data
current_date = int(datetime.datetime.now().timestamp())
list_of_game_names = db.smembers("gamelist")

for game in list_of_game_names:
    game = game.decode("utf-8")
    game_set_name = game + "-average_every_hour"

    # oldest timestamp is 30 days old
    current_time_plus_a_day = current_date - (60 * 60 * 24)
    current_time_plus_30_days = current_date - (60 * 60 * 24 * 30)
    db.zremrangebyscore(game_set_name, "-inf", current_time_plus_30_days)
    list_of_events = db.zrangebyscore(game_set_name, current_date, current_time_plus_a_day)

    if len(list_of_events) > 0:
        list_of_events = [int(float(x)) for x in list_of_events]
        average = sum(list_of_events) // len(list_of_events)
    else:
        average = 0

    if db.zadd(game + "-average_every_day", current_date, average) == 0:
        db.zadd(game + "-average_every_day", current_date, (repr(average) + "." + repr(current_date)))

print("Daily updates done. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
