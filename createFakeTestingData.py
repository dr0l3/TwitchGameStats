#!/usr/bin/python3
import urllib.request
import urllib.parse
import json
from datetime import timedelta
import datetime
import redis
import os
from random import randint

dbAddress = os.environ['DBADDRESS']
POOL = redis.ConnectionPool(host=dbAddress, port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)


def addmeasurementtodb(gamename, viewnumber, timestamp):
    db.sadd("gamelist", gamename)
    # append to the list
    if db.zadd(gamename + "-last_hour", timestamp, viewnumber) == 0:
        db.zadd(gamename + "-last_hour", timestamp, (repr(viewnumber) + "." + repr(timestamp)))


def addmeasurementtohourdb(gamename, viewnumber, timestamp):
    if db.zadd(gamename + "-average_every_hour", timestamp, viewnumber) == 0:
        db.zadd(gamename + "-average_every_hour", timestamp, (repr(viewnumber) + "." + repr(timestamp)))


def addmeasurementtodaydb(gamename, viewnumber, timestamp):
    if db.zadd(gamename + "-average_every_day", timestamp, viewnumber) == 0:
        db.zadd(gamename + "-average_every_day", timestamp, (repr(viewnumber) + "." + repr(timestamp)))


def createabunchoffakedata(gamename, startdate, minimum, maximum):
    currentdate = datetime.datetime.now()
    timedelta_30_days = timedelta(days=-30)
    timedelta_1_hour = timedelta(hours=-1)
    thirty_days_ago = (currentdate + timedelta_30_days)
    timestamp_thirty = datetime.datetime(thirty_days_ago.year, thirty_days_ago.month, thirty_days_ago.day).timestamp()
    one_hour_ago = (currentdate + timedelta_1_hour)
    timestamp_hour = datetime.datetime(one_hour_ago.year, one_hour_ago.month, one_hour_ago.day, one_hour_ago.hour, one_hour_ago.minute).timestamp()
    print(repr(thirty_days_ago))
    print(repr(one_hour_ago))
    print(repr(int(startdate.timestamp())) + " " + repr(int(timestamp_thirty)))
    print(repr(int(timestamp_thirty)) + " " + repr(int(timestamp_hour)))
    print(repr(int(startdate.timestamp())) + " " + repr(int(timestamp_thirty)))
    for ts in range(int(startdate.timestamp()), int(timestamp_hour), int(86400)):
        #print("day")
        addmeasurementtodaydb(gamename, randint(minimum, maximum), ts)

    for ts in range(int(timestamp_thirty), int(timestamp_hour), int(60*60)):
        #print("hour")
        addmeasurementtohourdb(gamename, randint(minimum, maximum), ts)

    for ts in range(int(timestamp_hour), int(currentdate.timestamp()), 60):
        #print("now")
        addmeasurementtodb(gamename, randint(minimum, maximum), ts)

    db.sadd("top_10_now", gamename)


createabunchoffakedata("ark", datetime.datetime(2015, 10, 10, 0, 0), 100, 2000)
createabunchoffakedata("world of warcraft", datetime.datetime(2015, 10, 10, 0, 0), 2000, 20000)
createabunchoffakedata("league of legends", datetime.datetime(2015, 10, 10, 0, 0), 80000, 200000)
createabunchoffakedata("dota 2", datetime.datetime(2015, 10, 10, 0, 0), 50000, 150000)
createabunchoffakedata("hearthstone", datetime.datetime(2015, 10, 10, 0, 0), 30000, 80000)
db.set("total_current_viewers", 500000)

print("Viewership numbers downloaded. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
