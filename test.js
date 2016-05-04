/**
 * Created by Rune on 04-05-2016.
 */

var date = new Date(1462351721*1000)
var utc_date = Date.UTC(date.getFullYear(), date.getMonth(), date.getDay(), date.getHours()+2, date.getMinutes())
console.log(date);
console.log(utc_date);
console.log("hello world");