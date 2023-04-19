import csv
import vincenty as vc

with open('../assets/simple_points.csv') as file:
    localities = csv.reader(file)
    next(localities)
    locs = []

    #for row in localities:
    #    locs.append(row)
    
    for loc in localities:
        print(loc[1])


# res = [(d['lat'], d['lon']) for d in locs]
