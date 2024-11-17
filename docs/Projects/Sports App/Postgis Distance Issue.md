- cartesian distance
- haversine distance
- geography type
```cs
public static class GeometryExtensions
    {
        // reference 1: https://rosettacode.org/wiki/Haversine_formula#C#
        // reference 2: https://stackoverflow.com/questions/41621957/a-more-efficient-haversine-function
        public static double CalculateHaversineDistance(this Point point, Point point2)
        {
            const double R = 6378100; // In meters
            var dLat = toRadians(point2.Y - point.Y);
            var dLon = toRadians(point2.X - point.X);

            var lat1 = toRadians(point.Y);
            var lat2 = toRadians(point2.Y);

            var a = Math.Sin(dLat / 2) * Math.Sin(dLat / 2) + Math.Sin(dLon / 2) * Math.Sin(dLon / 2) * Math.Cos(lat1) * Math.Cos(lat2);
            var c = 2 * Math.Asin(Math.Sqrt(a));
            return R * 2 * Math.Asin(Math.Sqrt(a));
        }

        public static double toRadians(double angle)
        {
            return Math.PI * angle / 180.0;
        }
    }
```

```cs
// todo: so far i have learned that .Distance() returns a value in cartesian coordinates

// we need it in meters

// we can use HaversineDistance formula to calculate in meters

// however, it can't be translated to SQL so we need another approach

// it turns out, we "could" use the `geography` type in postgres with [Column(TypeName="geography")]

// i will need to do this & test if the distance values for my test distances are 13m and 111km respectively
```

https://www.npgsql.org/efcore/mapping/nts.html?tabs=ef9-with-connection-string
https://learn.microsoft.com/en-us/ef/core/modeling/spatial
https://stackoverflow.com/questions/8464666/distance-between-2-points-in-postgis-in-srid-4326-in-metres
https://gis.stackexchange.com/questions/374604/what-are-degrees-in-srid-4326-and-why-cant-they-use-meters
https://gps-coordinates.org/distance-between-coordinates.php

challenge: users search for a location using google maps geocode API. the coordinates are sent to our backend. using the coordinates, find venues that are within a range of the defined location. 

problem: the code wasn't properly calculating the distance between defined location & the venues in the db. why?

cause: .Distance() calculates & returns distance in cartesian coordinates. Why? (Later found out this is due to the type of spatial data being used)

solution #1
haversine distance. This calculates the distance between two points on a sphere. Why is this helpful? You may have noticed the Earth is a sphere. 
However, this is not a complete solution. If we try to use this to query the database (include code sample), an exception is thrown because ef core can't translate the query to SQL. so, we need to try another approach.

solution #2. 
I did a lot of googling. I opened 10, 20 tabs. Then i saw a suggestion to try the geography data type. That uses geodedtic data, which means .Distance() calculates distance over a 3D sphere (rephrase this). 
Now we can query the database to find venues within a range (in meters) and get distance calculated in meters.
```cs
var userLocation = new Point(request.Longitude.Value, request.Latitude.Value) { SRID = 4326 };
                var rangeInMeters = (request.RangeInKm ?? 1.0) * 1000;
                query = query
                    .Select(v => new { Venue = v, Distance = v.Location.IsWithinDistance(userLocation, rangeInMeters) })
                    .Where(x => x.Distance)
                    .OrderBy(x => x.Distance);
```

# Article
Input - City Hall Park
Lat: 40.7128
Long: -74.0060

Venues
1. One World Trade Center
	- Long: -74.0134
	- Lat: 40.7127
	- Distance to input: 0.62km
2. Brooklyn Bridge
	- Long: -73.9969
	- Lat: 40.7061
	- Distance: 1.07km
3. Statue of Liberty
	- Long: -74.0445
	- Lat: 40.6892
	- Distance: 4.17km
4. Empire State Building
	- Long: -73.9857
	- Lat: 40.7488
	- Distance: 4.35km
5. Times Square
	- Long: -73.9855
	- Lat: 40.7580
	- Distance: 5.31km
6. Central Park
	- Long: -73.9654
	- Lat: 40.7851
	- Distance to input: 8.74km