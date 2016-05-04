#!/usr/bin/python3
import datetime
import redis
import functools
import os

dbAddress = os.environ["dbAddress"]
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

    #oldest timestamp is 30 days old
    current_time_plus_a_day = current_date + (60 * 60 * 24)
    current_time_plus_30_days = current_date + (60 * 60 * 24 * 30)
    db.zremrangebyscore(game_set_name, current_time_plus_30_days, "+inf")
    list_of_too_old_stuff = db.zrangebyscore(game_set_name, current_date, current_time_plus_a_day)

    if len(list_of_too_old_stuff) > 0:
        average = functools.reduce(add_two_numbers, [int(float(x)) for x in list_of_too_old_stuff]) // len(
                list_of_too_old_stuff)
    else:
        average = 0

    if db.zadd(game + "-average_every_day", current_date, average) == 0:
        db.zadd(game + "-average_every_day", current_date, (repr(average) + "." + repr(current_date)))

print("Daily updates done. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))