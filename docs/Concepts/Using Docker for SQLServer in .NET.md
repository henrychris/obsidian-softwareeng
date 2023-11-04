First things first, you need an SQLServer image to create a container from. You can use this commad to pull an image from the Docker Registry:
```
docker pull mcr.microsoft.com/mssql/server:2022-latest
```

You can also decide to download the image, create a container using said image AND start the container in one command, with this:

```
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=testPassword123@" -p 1433:1433 --name eventMgtDB --hostname eventMgtDB -d mcr.microsoft.com/mssql/server:2022-latest
```

- -p: Sets the port
- -e: Sets environment variables
	- ACCEPT_EULA: Self explanatory
	- MSSQL_SA_PASSWORD: Sets a password for the system admin, sa.
- -d: Runs the container in detached mode.
- --name: Sets the name for the container instance
- --hostname: Sets the name for the container when it is on a network.
- mcr.microsoft.com/mssql/server:2022-latest: The name of the image

The `docker run` command starts a SQL Server instance in a Docker container. There is a default database created as well, but that is not your concern. Next thing is to connect to the server and use a seeding script to create a database, and populate it with data if so desired. You could also connect to the DB using `sqlcmd`, but that is for another day.

Related: [[Connecting to a Dockerized SQLServer using sqlcmd]]

In appsettings, setup your connection string. It can be similar to this:
`Server=localhost;Database=EventDB;UserId=SA;Password=testPassword123@;MultipleActiveResultSets=true;TrustServerCertificate=true;`

Then, you need to seed your database. Check [[DB Seeding]]. This is what creates the database in the SQLServer instance.

After this is done, you can connect to your database using Azure Data Studio(or SSMS if you have RAM to waste). 

Related: [[Docker]]