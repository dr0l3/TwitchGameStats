#!/usr/bin/python3
from datetime import timedelta
import datetime
import redis
import functools
import os

dbAddress = os.environ["DBADDRESS"]
POOL = redis.ConnectionPool(host=dbAddress, port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)


def add_two_numbers(a, b):
    return a + b


def collapsehourly(game):
    starthour = 1
    current_time = datetime.datetime.now()
    while True:
        # get date one hour ago
        one_hour_ago = current_time - timedelta(hours=starthour)
        one_hour_ago_on_the_clock = datetime.datetime(one_hour_ago.year, one_hour_ago.month, one_hour_ago.day,
                                                      one_hour_ago.hour, 0)

        # get date two hours ago
        two_hours_ago = current_time - timedelta(hours=(starthour + 1))
        two_hours_ago_on_the_clock = datetime.datetime(two_hours_ago.year, two_hours_ago.month, two_hours_ago.day,
                                                       two_hours_ago.hour, 0)

        # get timestamps
        ts_start = two_hours_ago_on_the_clock.timestamp()
        ts_end = one_hour_ago_on_the_clock.timestamp() - 1

        # get data from db
        data_to_be_collapsed = db.zrangebyscore(game, ts_start, ts_end, withscores=True)
        starthour += 1
        if len(data_to_be_collapsed) > 1:
            # calculate the average
            total = 0
            total_ts = 0
            for viewcount_ts_tuple in data_to_be_collapsed:
                total += int(float(viewcount_ts_tuple[0].decode("utf-8")))
                total_ts += int(float(viewcount_ts_tuple[1]))
            average = total // len(data_to_be_collapsed)
            average_ts = total_ts // len(data_to_be_collapsed)

            # delete in db
            db.zremrangebyscore(game, ts_start, ts_end)

            # insert data in db
            db.zadd(game, average_ts, repr(average) + "." + repr(int(float(average_ts))))
        else:
            if len(data_to_be_collapsed) == 0:
                return
            else:
                continue

gamelist = db.smembers("gamelist")
for game in gamelist:
    collapsehourly(game)

print("Hourly updates done. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
