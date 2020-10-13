Data downloading and preparation

We use osm data. To download the data one option is: https://overpass-turbo.eu/

The data includes points and polygons. Therefore, we exclude these features using desired platform like geojson.io which enables edit and export our geojson data.

Database

We initialize our Django app by install psycopg2-binary, Django, leaflet and also create our database and import our database configurations into our Django application.
In our database, we install postgis and pgrouting extensions.

Measuring Road Length

We can do this calculation both in psql shell or in QGIS. To calculate road length in QGIS we first add the postgis cdatabase connection and then in db manager ion the sql window we insert and run the query:

update paris_routes set roadLength = ST_Length(ST_Transform(geom,26986))

Create Topology

To create the network topology, first we add to columns into our table:

ALTER TABLE paris_routes ADD COLUMN source INT4;
ALTER TABLE paris_routes ADD COLUMN target INT4;

Our line data are not noded. It means that the start and end of our line segments are not specified. It is used for creating topology. To do that:
First we create the topology:
pgr_createTopology('edge_table',0.001,'geom','id','source','target','true')
and then :

SELECT pgr_nodeNetwork('edge_table', 0.001);

In which id and geom are column names in our table. After that a noded column is created with an added ‘noded’ to the original name. So, the new table name would be: 'paris_routes_noded'

Then we create topology over created noded network:

SELECT pgr_createTopology('paris_routes_noded', 0.00001, 'geom');

Cost function

It is important to first determine costing mechanism and the cost attributes based on customer need and goal. Every edge gets a weighting. Mostly this is the distance, but can also be travel duration or something else. Then algorithms like Dijkstra or A* find the shortest path by minimizing the sum of the weightings.

For instance, we set road length as our cost attribute. To do that, we create a column in our noded network:

ALTER TABLE paris_routes_noded ADD dist FLOAT;
UPDATE paris_routes_noded SET dist = st_length(st_transform(geom, 26986));

Then, the column “dist” is created which assign length of each segment as the cost attribute of the segment.


Loading data in our platform

We are going to load our shapefile “paris_routes_noded” with all the attributes in our python app. We will first query our data and turn our data to geojson file:

topoQuery = connection.cursor()
topoQuery.execute("SELECT jsonb_build_object('type', 'FeatureCollection','features', jsonb_agg(features.feature)) FROM (SELECT jsonb_build_object('type', 'Feature','geometry', ST_AsGeoJSON(geom)::jsonb,'properties', to_jsonb(inputs) ) AS feature FROM (SELECT * FROM paris_routes) inputs) features;")
topoResult = topoQuery.fetchall()


This part (select * from paris_routes) will return the whole dataset with all roads as a geojson file format.

Dijkstra algorithm

The algorithm gets the source, target and cost as inputs and returns the shortest path.

select MIN(r.seq) as seq, e.old_id AS id, sum(e.dist) AS dist, st_collect(e.geom) as geom from pgr_dijkstra('select id, source, target, dist as cost from paris_routes_noded', 4, 15, false) as r, paris_routes as e where r.edge = e.id GROUP BY e.old_id

So, in our table instead of (select * from paris_route) we should import the Dijkstra query to return just the queried path or shortest path:

lineQuery = connection.cursor()
 lineQuery.execute("SELECT jsonb_build_object('type', 'FeatureCollection','features', jsonb_agg(features.feature)) FROM (SELECT jsonb_build_object('type', 'Feature','geometry', ST_AsGeoJSON(geom)::jsonb,'properties', to_jsonb(inputs) ) AS feature FROM (select MIN(r.seq) as seq, e.old_id AS id, sum(e.dist) AS dist, st_collect(e.geom) as geom from pgr_dijkstra('select id, source, target, dist as cost from paris_routes', 4, 15, false) as r, paris_routes as e where r.edge = e.id GROUP BY e.old_id) inputs) features;")
lineResult = lineQuery.fetchall()

Then, we will send the dataset to javascript and can be read by leaflet and added as a feature.

It should be noted that the id, source and target datatype should be bigint, otherwise the algorithm returns error. To alter column data type:

alter table paris_routes alter column source type bigint;


Adding source and target markers

We add source and target markers which are draggable and then the coordinates to our python view to specify source and target interactively.
var sourceLat, sourceLon, targetLat, targetLon;
            var sourceMarker = L.marker([48.848874, 2.416867], {draggable:'true'}).on('dragend', function(event) {
                var latlng = event.target.getLatLng();
                sourceLat = latlng.lat;
                sourceLon = latlng.lng;
            }).addTo(map);
            var targetMarker = L.marker([48.846952, 2.427172], {draggable:'true'}).on('dragend', function(event) {
                var latlng = event.target.getLatLng();
                targetLat = latlng.lat;
                targetLon = latlng.lng;
            }).addTo(map);

The next step is to send the retrieved coordinates to the python view using ajax:
In javascript we add ajax in our dragged update function:

var sourceLat, sourceLon, targetLat, targetLon;
            // getting lat lng of the marker and sending to django view with ajax
            var sourceMarker = L.marker([48.848874, 2.416867], {draggable:'true'}).on('dragend', function(event) {
                var latlng = event.target.getLatLng();
                sourceLat = latlng.lat;
                sourceLon = latlng.lng;
                $.ajax({
                    url: '', //it means send it to the root url that was set before
                    data: {
                        'sourceLat': sourceLat,
                        'sourceLon': sourceLon,
                        'targetLat': sourceLat, // we also send the target position to avoid non value in python view
                        'targetLon': sourceLon,

                    },
                    dataType: 'json',
                    success: function (data) {
                        if (data.is_taken) {
                            alert("A user with this username already exists.");
                        }
                }
            });
            }).addTo(map);
            var targetMarker = L.marker([48.846952, 2.427172], {draggable:'true'}).on('dragend', function(event) {
                var latlng = event.target.getLatLng();
                targetLat = latlng.lat;
                targetLon = latlng.lng;
                $.ajax({
                    url: '', //it means send it to the root url that was set before
                    data: {
                        'sourceLat': sourceLat,
                        'sourceLon': sourceLon,
                        'targetLat': sourceLat,
                        'targetLon': sourceLon,
                    },
                    dataType: 'json',
                    success: function (data) {
                        if (data.is_taken) {
                            alert("ok");
                        }
                    }    
                });
            }).addTo(map);

And in our python view we simply get the data send from ajax or we can define a form which user can specify source and target and submit the form:

sourceLat = request.GET.get('sourceLat')
sourceLon = request.GET.get('sourceLon')
targetLat = request.GET.get('targetLat')
targetLon = request.GET.get('targetLon')



One of the benefit of AJAX is that it prevents page reload when we submit or send a variable to python view. While, when we use html form, it reloads the page.


Finding nearest source point

Here, we have the topology point layer. So, we find the nearest points from previously user-defined source and target coordinates using ST_Distance function and we retrieve the source id and target id of nearest points to the user-defined points by ordering them by computed distance and retrieve the first element of the resulted array:

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


We make use of the sourceId and targetId as inputs in our routing query:
lineQuery = connection.cursor()
        lineQuery.execute("SELECT jsonb_build_object('type', 'FeatureCollection','features', jsonb_agg(features.feature)) FROM (SELECT jsonb_build_object('type', 'Feature','geometry', ST_AsGeoJSON(geom)::jsonb,'properties', to_jsonb(inputs) ) AS feature FROM (select MIN(r.seq) as seq, e.old_id AS id, sum(e.dist) AS dist, st_collect(e.geom) as geom from pgr_dijkstra('select id, source, target, dist as cost from paris_routes', %s, %s, false) as r, paris_routes as e where r.edge = e.id GROUP BY e.old_id) inputs) features;", (sourceId, targetId,))
        lineResult = lineQuery.fetchall()
        nn = json.dumps(lineResult)

Normalized Cost 

To use normalized value of attribute as cost value, we just simply use from min-max normalization method. We create a colum named “cost”:
alter table paris_routes add column cost double precision;

and then specify the value based on distance attribute:

update paris_routes set cost = (dist- (select MIN(dist) from paris_routes))/((select MAX(dist) from paris_routes) - (select MIN(dist) from paris_routes));

The same strategy can be applied when we have multiple attribute for determining the cost value. In this case we can simply sum up the values.
