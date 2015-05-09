"""
Process the GTFS feed, and find headings from standing in the middle of the street to the transit stop.
This is so that we can create a Google Street View looking at the stop.

It uses the direction of the route to estimate the heading.
"""

import csv
import json
from math import cos, atan2

stops = dict()

def calcBearing(lat1, lon1, lat2, lon2):
    # do an equirectangular projection
    xscale = cos(lat1 * 3.1415926 / 180)

    lon1 = lon1 * xscale
    lon2 = lon2 * xscale

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    if abs(dlon) < 0.000000001:
        if dlat < 0:
            return 180
        else:
            return 0

    return atan2(dlon, dlat) * 180 / 3.14159

# load stops
with open('stops.txt') as stopTxt:
    stopsCsv = csv.DictReader(stopTxt)

    for stop in stopsCsv:
        stops[stop['stop_id']] = stop

# load trips to find direction of travel
trips = dict()

with open('stop_times.txt') as stTxt:
    stCsv = csv.DictReader(stTxt)

    for st in stCsv:
        if not trips.has_key(st['trip_id']):
            trips[st['trip_id']] = []

        trips[st['trip_id']].append((st['stop_id'], st['stop_sequence']))

# Sort trips by stop sequence
for trip_id, trip in trips.iteritems():
    trip = sorted(trip, key=lambda x: x[1])

    for i in range(0, len(trip)):
        if i > 0:
            # if not first stop, there is a previous stop
            prev = trip[i - 1][0]
        else:
            prev = None

        if i < len(trip) - 1:
            nxt = trip[i + 1][0]
        else:
            nxt = None

        stop = stops[trip[i][0]]

        # We always want to use previous and nxt from the same route,
        # and prefer having both. We never want to mix routes. Consider
        # for example at Washington Hospital Center where the H uses the
        # same stop on 1st NW just inside the gate both inbound and outbound
        if not (stop.has_key('prev') and stop.has_key('nxt')) and\
            prev is not None and nxt is not None:
            stop['prev'] = prev
            stop['nxt'] = nxt

        elif not stop.has_key('prev') and prev is not None:
            stop['prev'] = prev
            stop['nxt'] = None

        elif not stop.has_key('nxt') and nxt is not None:
            stop['nxt'] = nxt
            stop['prev'] = None

# print 'lat,lon,heading'

for stopId, stop in stops.iteritems():
    # find the previous and nxt stops, figure out the bearing
    if not (stop.has_key('prev') and stop.has_key('nxt') and stop['prev'] is not None and stop['nxt'] is not None):
        # TODO handle stops that don't have both nxt and prev (i.e. terminal stops)
        continue

    prevLat = float(stops[stop['prev']]['stop_lat'])
    prevLon = float(stops[stop['prev']]['stop_lon'])
    cLat = float(stop['stop_lat'])
    cLon = float(stop['stop_lon'])
    nxtLat = float(stops[stop['nxt']]['stop_lat'])
    nxtLon = float(stops[stop['nxt']]['stop_lon'])

    prevBearing = opb = calcBearing(prevLat, prevLon, cLat, cLon)
    nextBearing = calcBearing(cLat, cLon, nxtLat, nxtLon)

    # This just takes a tangent from the previous stop.
    # TODO: use next stop as well
    stop['heading'] = (prevBearing + 90) % 360

    #print str(cLat) + ',' + str(cLon) + ',' + str(stop['heading'])

# Some stops don't have headings, ignore them
json.dump([v for k, v in stops.iteritems() if v.has_key('heading')], open('stops.json', 'w'))
