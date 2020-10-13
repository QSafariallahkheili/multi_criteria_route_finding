
Three parameters have been included to determine cost attribute of the routes including population density, covid infection rate per 10000 poulation and road length.

. Population density (square kilometer)

Alter table area add column area double precision;

update covid set area = (select st_area(st_transform(geom, 26986)));

So, we can compute the population density for each polygon and assign it to the roads which intersect the polygon.

To calculate population density, we use simply update query and use from column names that we want to use for our calculation:

Update covid set popsensity = (poplation*1000000)/(area)

This computes the population density per square kilometer unit.


. Case per 10000 population

The same procedure is done for calculation covid case per 10000 population

Assign polygon attributes to roads

To join attributes of polygon features to line and roads features, one road may cross from multiple polygons. To overcome this problem, we split lines which intersect polygons. In QGIS:
Vector -->geoprocessing tools --> intersection

The next step is to assign polygon attributes to line features which intersect each polygon. This method, joins the attributes of the polygon to the line which intersects the polygon

The other option is:
Vector-->data management tools-->join attributes by location and set the geometry predicate as “intersects” 


. Road Length

We calculate the length of each road segment:
ALTER TABLE roads_intersect ADD length FLOAT;
UPDATE roads_intersect SET length = st_length(st_transform(geom, 26986));

It computes the length of road segments in meters.

. Compute cost

To compute cost we use the normalized value of population density, infection rate and length. And finally we simply sum up these value and assign it to line segments.

update roads_intersect set totcost = (lengthnormal+popdennormal+infratenormal);

Create Topology

To create the network topology, first we add to columns into our table:

ALTER TABLE roads_intersect ADD COLUMN source INT4;
ALTER TABLE roads_intersect ADD COLUMN target INT4;

Our line data are not noded. It means that the start and end of our line segments are not specified. It is used for creating topology. To do that:

SELECT pgr_nodeNetwork(‘roads_intersect ', 0.00001, 'geom');

In which id and geom are column names in our table. After that a noded column is created with an added ‘noded’ to the original name. So, the new table name would be: 'paris_routes_noded'

Then we create topology over created noded network:

pgr_createTopology('edge_table',0.001,'geom','id','source','target','true')
and then :

SELECT pgr_nodeNetwork('edge_table', 0.001);


Finding nearest source and sarget point

Here, we have the topology point layer. So, we find the nearest points from previously user-defined source and target coordinates using ST_Distance function and we retrieve the source id and target id of nearest points to the user-defined points by ordering them by computed distance and retrieve the first element of the resulted array.

Finally the Dijekstra algorithm is used which gets the source, target and cost as input and returns the shortest path.


