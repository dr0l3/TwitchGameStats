import pickle
import operator

with open("GameHistory", "rb") as f:
    listofgames = pickle.load(f)

averages = {}
for game in listofgames:
    total = 0
    n = 0
    for measurement in listofgames[game]:
        viewers, date = measurement
        total += viewers
        n += 1
    average = total/n
    averages[game] = average

sorted_averages = sorted(averages.items(), key=operator.itemgetter(1), reverse=True)
for line in sorted_averages:
    print(line)
