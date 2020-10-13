from django.shortcuts import render
from .models import Routes, Vertices
from django.contrib.gis.utils import LayerMapping
from django.core.serializers import serialize
from django.db.models import Sum
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D, Distance
import re
from django.db import connection
import os
import json
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.template import RequestContext, Template



def indexPage(request):
    
    
    """
    query = Routes.objects.all()
    routes = serialize("geojson", query)
    """
    points = 1
    nn = 1
    user_lat = 48.848874
    user_lon = 2.416867
    
    user_latt = 48.846952
    user_lonn = 2.427172
   

    if request.method=='POST' and 'sourceLatt' and 'targetLatt' in request.POST:
        user_lat = request.POST.get('sourceLatt', 48.848874)
        #user_lat1 = float(user_lat.replace(',',''))
        user_lon = request.POST.get('sourceLonn', 2.416867)
        #user_lon1 = float(user_lon.replace(',',''))
        user_latt = request.POST.get('targetLatt', 48.846952)
        #user_latt1 = float(user_latt.replace(',',''))
        user_lonn = request.POST.get('targetLonn', 2.427172)
        #user_lonn1 = float(user_lonn.replace(',',''))
        print(user_lat, user_lon)
    # retrieving coordinates of source and target
    
        sourceLat = request.GET.get('sourceLat', 48.848874) # here we iitialize lat and lng because as the page is loaded the markers are not moved and the result is Non
        sourceLon = request.GET.get('sourceLon', 2.416867)
        targetLat = request.GET.get('targetLat', 48.846952)
        targetLon = request.GET.get('targetLon', 2.427172)
        #print(sourceLat, sourceLon, targetLat, targetLon)
        #print("marker lat is: ", sourceLat, "marker lon is: ", sourceLon)

        #retrieving the source id 
        #if request.method == "POST":
    

        sourceQuery = connection.cursor()
        sourceQuery.execute("select topo.id from paris_topology topo order by ST_Distance(st_transform(topo.geom, 26986), st_transform(ST_SetSRID(ST_MakePoint(%s,%s),4326), 26986)) ASC;", (user_lon, user_lat,))
        sourceResult = sourceQuery.fetchall()
        sourceIdArray = [item for t in sourceResult for item in t] 
        sourceId = sourceIdArray[0]
        #print("sourceId", sourceId)

        #retrieving the target id 
        targetQuery = connection.cursor()
        targetQuery.execute("select topo.id from paris_topology topo order by ST_Distance(st_transform(topo.geom, 26986), st_transform(ST_SetSRID(ST_MakePoint(%s,%s),4326), 26986)) ASC;", (user_lonn, user_latt,))
        targetResult = targetQuery.fetchall()
        targetIdArray = [item for t in targetResult for item in t] 
        targetId = targetIdArray[0]
        #print("targetId", targetId)

        # now we put the retrieved target and source id inside our query
        lineQuery = connection.cursor()
        lineQuery.execute("SELECT jsonb_build_object('type', 'FeatureCollection','features', jsonb_agg(features.feature)) FROM (SELECT jsonb_build_object('type', 'Feature','geometry', ST_AsGeoJSON(geom)::jsonb,'properties', to_jsonb(inputs) ) AS feature FROM (select MIN(r.seq) as seq, e.old_id AS id, sum(e.dist) AS dist, st_collect(e.geom) as geom from pgr_dijkstra('select id, source, target, cost as cost from paris_routes', %s, %s, false) as r, paris_routes as e where r.edge = e.id GROUP BY e.old_id) inputs) features;", (sourceId, targetId,))
        lineResult = lineQuery.fetchall()
        nn = json.dumps(lineResult)


        topoQuery = connection.cursor()
        topoQuery.execute("SELECT jsonb_build_object('type', 'FeatureCollection','features', jsonb_agg(features.feature)) FROM (SELECT jsonb_build_object('type', 'Feature','geometry', ST_AsGeoJSON(geom)::jsonb,'properties', to_jsonb(inputs) ) AS feature FROM (SELECT * FROM paris_topology) inputs) features;")
        topoResult = topoQuery.fetchall()
        points = json.dumps(topoResult)
    else:


        # now we put the retrieved target and source id inside our query
        lineQuery = connection.cursor()
        lineQuery.execute("SELECT jsonb_build_object('type', 'FeatureCollection','features', jsonb_agg(features.feature)) FROM (SELECT jsonb_build_object('type', 'Feature','geometry', ST_AsGeoJSON(geom)::jsonb,'properties', to_jsonb(inputs) ) AS feature FROM (SELECT * FROM paris_routes) inputs) features;")
        lineResult = lineQuery.fetchall()
        nn = json.dumps(lineResult)


        topoQuery = connection.cursor()
        topoQuery.execute("SELECT jsonb_build_object('type', 'FeatureCollection','features', jsonb_agg(features.feature)) FROM (SELECT jsonb_build_object('type', 'Feature','geometry', ST_AsGeoJSON(geom)::jsonb,'properties', to_jsonb(inputs) ) AS feature FROM (SELECT * FROM paris_topology) inputs) features;")
        topoResult = topoQuery.fetchall()
        points = json.dumps(topoResult)

    context = {
            'points':points,
            'nn':nn,
            'user_lat': user_lat,
            'user_lon': user_lon,
            'user_latt': user_latt,
            'user_lonn': user_lonn,
    }
    return render(request, "index.html", context)
    

    


    
    
    

