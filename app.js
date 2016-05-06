var http = require('http');
var Promise = require('promise');
var redis = require('redis');
var client = redis.createClient();
var express = require('express');
var path = require('path');
var util = require('util');
var fs = require('fs');
var app = express();

function nth_occurrence (string, char, nth) {
    var first_index = string.indexOf(char);
    var length_up_to_first_index = first_index + 1;

    if (nth == 1) {
        return first_index;
    } else {
        var string_after_first_occurrence = string.slice(length_up_to_first_index);
        var next_occurrence = nth_occurrence(string_after_first_occurrence, char, nth - 1);

        if (next_occurrence === -1) {
            return -1;
        } else {
            return length_up_to_first_index + next_occurrence;
        }
    }
}

function extractdatefromdbstring(string){
    var year = parseInt(string.substring(nth_occurrence(string,"(",2)+1, nth_occurrence(string,"(",2)+5));
    var month = parseInt(string.substring(nth_occurrence(string,",",2)+1, nth_occurrence(string,",",3))) - 1;
    var day = parseInt(string.substring(nth_occurrence(string,",",3)+1, nth_occurrence(string,",",4)));
    var hour = parseInt(string.substring(nth_occurrence(string,",",4)+1, nth_occurrence(string,",",5)));
    var minute = parseInt(string.substring(nth_occurrence(string,",",5)+1, nth_occurrence(string,",",6)));
    var second = parseInt(string.substring(nth_occurrence(string,",",6)+1, nth_occurrence(string,",",7)));
    return Date.UTC(year, month, day, hour, minute, second);
}

function getOnlyLatestGameDataFromDB(data){
    return new Promise(function( resolve, reject){
        var gameStats = {};
        gameStats["name"] = data;

        client.zrevrange(data, "0", "0", function (err, replies) {
            if (err) {
                console.log("Err in data connection to Redis: " + err);
                gameStats["data"] = 0;
                resolve(gameStats);
            }

            gameStats["data"] = parseInt(replies);

            resolve(gameStats);
        });
    });
}

function getGameDataFromDBForLastHour(game){
    return new Promise(function (resolve, reject){
        var gamestats = {};
        gamestats["name"] = game;
        var viewnumbers = [];
        var ts_now = Date.now();
        //Timestamps in the db are python timestamps that aren't in miliseconds.
        ts_now = ts_now / 1000;
        var ts_an_hour_ago = ts_now - (60*60);


        client.zrangebyscore(game, ts_an_hour_ago, ts_now, "withscores", function(err, replies){
            if(err){
                console.log("Err in data connection to Redis: " + err);
                resolve({});
            }

            for (var i = 0; i < replies.length; i = i +2){
                viewnumbers.push([replies[i+1]*1000, parseInt(replies[i])]);
            }

            gamestats["data"] = viewnumbers;
            resolve(gamestats);
        });
    });
}

function getGameDataFromDBUsingRange(game, start_ts, end_ts){
    return new Promise(function (resolve, reject){
        var gamestats = {};
        gamestats["name"] = game;
        var viewnumbers = [];

        client.zrangebyscore(game, start_ts, end_ts, "withscores", function(err, replies){
            if(err){
                console.log("Err in data connection to Redis: " + err);
                resolve({});
            }

            for (var i = 0; i < replies.length; i = i +2){
                viewnumbers.push([replies[i+1]*1000, parseInt(replies[i])]);
            }

            gamestats["data"] = viewnumbers;

            resolve(gamestats);
        });
    });
}

function getGameDataFromDB(data) {
    return new Promise(function (resolve, reject) {
        var gameStats = {};
        gameStats["name"] = data;
        var viewNumbers = [];

        client.zrange(data, "0", "-1","withscores", function (err, replies) {
            if (err) {
                console.log("Err in data connection to Redis: " + err);
                resolve({});
            }

            for (var i = 0; i < replies.length; i = i+2){
                viewNumbers.push([replies[i+1]*1000, parseInt(replies[i])]);
            }

            gameStats["data"] = viewNumbers;

            resolve(gameStats);
        });
    });
}

function getTotalViewersFromDB(){
    return new Promise(function(resolve, reject){
        client.get("total_current_viewers", function(err, reply){
            if (err){
                console.log("Err in data connection to Redis: " + err);
                resolve(0);
            }
            resolve(reply);
        });
    });
}

function getviewernumbersfromstring(gamename){
    client.lrange(gamename, "0", "-1", function(err, replies){
        var viewernumbers = [];
        replies.forEach(function (reply, i){
            data["name"] = gamename;
            viewernumbers.push([extractdatefromdbstring(reply), parseInt(reply.substring(1,reply.indexOf(",")))]);
        });
        data["data"] = viewernumbers;
        return data;
    });
}

function removewhitespace(string){
    return string.replace(/\s+/, "");
}

function uniq_fast(a) {
    var seen = {};
    var out = [];
    var len = a.length;
    var j = 0;
    for(var i = 0; i < len; i++) {
        var item = a[i];
        if(seen[item] !== 1) {
            seen[item] = 1;
            out[j++] = item;
        }
    }
    return out;
}

function getgamelist(){
    return new Promise(function(resolve,reject){
        //do get the game list
        //resolve(gamelist);
    });
}

function getgameJSON(gamelist){
    return new Promise(function(resolve,reject){
        //get the stuffs
        //resolve(json);
    });
}

//do redis.keys to get list of gamelists
//do redis.lrange to get list of
//send the stuff
app.get('/stuff', function(req, res){
    var gamelist = getgamelist();
    gamelist.then(getgameJSON(gamelist)).then(function(JSON){
        //send the JSON?
    });
});

app.get('/gamezoom/*', function(req, res){
    var game = req.originalUrl.substring(nth_occurrence(req.originalUrl, "/", 2)+1, req.originalUrl.len);
    res.sendFile('individualZoomable.html', { root: path.join(__dirname, './public') });
});

app.get('/game/*', function(req, res){
    var game = req.originalUrl.substring(nth_occurrence(req.originalUrl, "/", 2)+1, req.originalUrl.len);
    res.sendFile('individualGame.html', { root: path.join(__dirname, './public') });
});

app.get('/', function(req, res){
    res.sendFile('abc.html', { root: path.join(__dirname, './public') });
});

app.get('/public/gamelist.json*', function(req, res){
    var query = req.query["q"];
    new Promise(function(resolve, reject){
        client.sscan("gamelist",0, "MATCH", "*"+query+"*", "COUNT", "1000", function(err, replies){
            var games = [];
            replies = replies[1];
            replies.forEach(function(reply, i){
                games.push({"value": reply, "label": reply})
            });
            resolve(games);
        });
    }).then(function(data){
        res.send(data);
    });
});

app.get('/public/lasthourPie.json', function(req, res){
    new Promise(function(resolve, reject) {
        client.smembers("top_10_now", function(err, replies){
            var games = [];
            replies.forEach(function(reply, i){
                games.push(reply);
            });
            //console.log(games);
            resolve(games);
        });
    }).then(function(data){
        var list_of_promises = data.map(getOnlyLatestGameDataFromDB);
        //list_of_promises.push(getTotalViewersFromDB());
        return Promise.all(list_of_promises);
    }).then(function(data){
        return new Promise(function(resolve, reject){
            var viewernumbers = getTotalViewersFromDB();
            viewernumbers.then(function(data3){
                resolve({"gamenumbers": data, "totalviewers" : data3});
            });
        });
    }).then(function(data){
        var gameData = [];
        var total_top_ten = 0;
        for (var i = 0; i < data["gamenumbers"].length; i++){
            var viewerNumber = data["gamenumbers"][i]["data"];
            var gameName = data["gamenumbers"][i]["name"];
            total_top_ten = total_top_ten + viewerNumber;
            gameData.push(
                {
                    "name": gameName,
                    "y": viewerNumber
                }
            );
        }
        var rest = data["totalviewers"] - total_top_ten;
        gameData.push({"name": "Rest", "y" : rest});
        var retval = [{
            "name": "games",
            "colorByPoint": true,
            "data": gameData
        }];
        res.send(retval);
    });
});

app.get('/public/lasthour.json', function(req, res){

    //Find all game titles
    var gamelist = new Promise(function(resolve, reject) {
        client.smembers("top_10_now", function(err, replies){
            var games = [];
            replies.forEach(function(reply, i){
                games.push(reply);
            });
            resolve(games);
        });
    });

    //find viewer numbers for each game
    var more_res = gamelist.then(function(data){
        return Promise.all(data.map(getGameDataFromDBForLastHour));
    });

    //send the page
    more_res.then(function(data){
        res.send(data);
    });
});

app.get('/public/individualgame.json', function(req, res){
    var query = req.query;
    console.log(query);
    var game = query["game"];
    var duration = query["duration"];
    var gamelist = game;
    console.log(gamelist);
    var data = new Promise(function(resolve, reject){
        client.zrange(gamelist, 0, -1, "withscores", function(err, replies){
            var gamedata = {};
            gamedata["name"] = game;
            var viewnumbers = [];

            if (err){
                console.log("Err in data connection to Redis: " + err);
            }

            for (var i = 0; i < replies.length; i = i+2){
                viewnumbers.push([replies[i+1]*1000, parseInt(replies[i])]);
            }

            gamedata["data"] = viewnumbers;

            resolve(gamedata);
        });
    });
    data.then(function(data){
        //console.log(data);
        res.send([data]);
    })
});


client.on('connect', function() {
    console.log('connected');
});

var server = app.listen(5000, function(){
    var host = server.address().address;
    var port = server.address().port;

    console.log('example app listen at https://%s:%s', host,port);
});