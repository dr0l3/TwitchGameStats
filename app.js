var http = require('http');
var Promise = require('promise');
var redis = require('redis');
var client = redis.createClient();
var express = require('express');
var path = require('path');
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

function getGameDataFromDB(data) {
    return new Promise(function (resolve, reject) {
        var gameStats = {};
        gameStats["name"] = data;
        var viewNumbers = [];

        client.zrange(data+"-last_hour", "0", "-1","withscores", function (err, replies) {
            if (err) {
                console.log("Err in data connection to Redis: " + err);
                resolve({});
            }
            //console.log(replies);

            for (var i = 0; i < replies.length; i = i+2){
                var date = new Date(replies[i+1]*1000);
                var date_in_utc = Date.UTC(date.getFullYear(), date.getMonth(), date.getDay(), date.getHours(), date.getMinutes());

                viewNumbers.push([date_in_utc, parseInt(replies[i])]);
            }


            gameStats["data"] = viewNumbers;
            console.log(gameStats)

            //console.log(replies);
            resolve(gameStats);
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

app.get('/game/*', function(req, res){
    var game = req.originalUrl.substring(nth_occurrence(req.originalUrl, "/", 2)+1, req.originalUrl.len);
    console.log(game);

});

app.get('/', function(req, res){
    res.sendFile('abc.html', { root: path.join(__dirname, './public') });
});

app.get('/public/lasthour.json', function(req, res){

    //Find all game titles
    var gamelist = new Promise(function(resolve, reject) {
        client.smembers("top_10_now", function(err, replies){
            var games = [];
            replies.forEach(function(reply, i){
                games.push(reply);
            });
            //console.log(games);
            resolve(games);
        });
    });

    //find viewer numbers for each game
    var more_res = gamelist.then(function(data){
        return Promise.all(data.map(getGameDataFromDB));
    });

    //send the page
    more_res.then(function(data){
        //console.log(data);
        res.send(data);
    });
});


client.on('connect', function() {
    console.log('connected');
});

var server = app.listen(5000, function(){
    var host = server.address().address;
    var port = server.address().port;

    console.log('example app listen at https://%s:%s', host,port);
});