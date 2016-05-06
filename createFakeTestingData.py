#!/usr/bin/python3
from datetime import timedelta
import datetime
import redis
import os
from random import randint

dbAddress = os.environ['DBADDRESS']
POOL = redis.ConnectionPool(host=dbAddress, port=6379, db=0)
db = redis.StrictRedis(connection_pool=POOL)


def printdatatofile(gamename):
    itemlist = db.zrange(gamename, 0, -1, withscores=True)
    # print(itemlist)
    file = open('datapython.json', 'w+')
    file.writelines(
            ["%s\n" % datetime.datetime.utcfromtimestamp(item[1]).strftime("%Y-%m-%d %H:%M:%S") for item in itemlist])


def addmeasurementtodb(gamename, timestamp, viewnumber, ):
    # append to the list
    db.zadd(gamename, timestamp, repr(viewnumber) + "." + repr(int(float(timestamp))))


def createabunchoffakedata(gamename, startdate, minimum, maximum):
    currentdate = datetime.datetime.now()
    delta = datetime.timedelta(minutes=1)
    iterdate = startdate
    while iterdate <= currentdate:
        # print(iterdate)
        addmeasurementtodb(gamename, repr(iterdate.timestamp()), randint(minimum, maximum))
        iterdate += delta

    db.sadd("top_10_now", gamename)
    db.sadd("gamelist", gamename)


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


def collapsedaily(game):
    startday = 30
    current_time = datetime.datetime.now()
    while True:
        # get date one hour ago
        one_day_ago = current_time - timedelta(days=startday)
        one_day_ago_at_midnight = datetime.datetime(one_day_ago.year, one_day_ago.month, one_day_ago.day,
                                                    0, 0)

        # get date two hours ago
        two_days_ago = current_time - timedelta(days=(startday + 1))
        two_days_ago_at_midnight = datetime.datetime(two_days_ago.year, two_days_ago.month, two_days_ago.day,
                                                     0, 0)
        # get timestamps
        ts_start = two_days_ago_at_midnight.timestamp()
        ts_end = one_day_ago_at_midnight.timestamp() - 1

        # get data from db
        data_to_be_collapsed = db.zrangebyscore(game, ts_start, ts_end, withscores=True)
        startday += 1
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


db.set("total_current_viewers", 20000)
createabunchoffakedata("ark", datetime.datetime(2016, 3, 1, 10, 55), 100, 2000)
print("Data created")
createabunchoffakedata("world of warcraft", datetime.datetime(2016, 3, 1, 10, 55), 2000, 20000)
# createabunchoffakedata("league of legends", datetime.datetime(2015, 10, 10, 0, 0), 80000, 200000)
# createabunchoffakedata("dota 2", datetime.datetime(2015, 10, 10, 0, 0), 50000, 150000)
# createabunchoffakedata("hearthstone", datetime.datetime(2015, 10, 10, 0, 0), 30000, 80000)
# db.set("total_current_viewers", 500000)
collapsehourly("ark")
collapsehourly("world of warcraft")
print("Hourly updates done")
collapsedaily("ark")
collapsedaily("world of warcraft")
print("Daily updates done")
# printdatatofile("ark")

print("Viewership numbers downloaded. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
