---
share: "true"
---
Database seeding is a process in which you populate your database with initial or default data when your application starts. This initial data could include default records, sample data, or any data necessary for the application to function correctly during development or testing.

**SeedDataBase.cs:**
- This method is designed to populate the `EventModule` database with initial data. It only runs when the application is in the development environment.
- It uses a service scope to access the `EventDbContext`. The method then performs several operations:
    - **Deletes the database**: It calls [[#EnsureDatabaseDeletedAsync]] to delete the existing database, if it exists. This ensures a clean slate for seeding.
    - **Creates the database**: It calls [[#EnsureCreatedAsync]] to create a new database or re-creates it from your Entity Framework model.
    - **Adds sample data**: Adds a sample event record to the database if it doesn't already exist.

**Note**: There was an error related to using *relational* methods on an in-memory database. I switched to SQLServer for development, and use an in-memory database for testing. So, I made an adjustment to the seeding script. We ensure created when testing as we only want the database structure. For development, we only apply migrations to keep the data intact.

```
public static async Task SeedDatabase(this WebApplication app)  
{  
    if (app.Environment.IsDevelopment())  
    {        
	    Console.WriteLine("Starting EventModule database seeding.");  
        using var scope = app.Services.CreateScope();  
  
        var context = scope.ServiceProvider.GetRequiredService<EventDbContext>();  
        if (IsInMemoryDatabase(context))  
		{  
		    await context.Database.EnsureDeletedAsync();  
			await context.Database.EnsureCreatedAsync();  
			await SeedEvents(context);
		}  
		else  
		{  
		    await context.Database.MigrateAsync();  
			await SeedEvents(context);  
		}
        await context.SaveChangesAsync();  
        Console.WriteLine("EventModule database seeding complete.");  
    }
}
```

**`UseEventModule` Extension Method**:
- This extension method is intended to be used in the application startup. It calls the `SeedDatabase` method, which, in turn, seeds the `EventModule` database.
```
public static void UseEventModule(this WebApplication app)  
{  
    app.SeedDatabase().Wait();  
}
```

**`ConfigureApplication` Method**:
- This method is responsible for configuring various aspects of the web application, including registering Swagger, setting up middleware, and registering modules. It calls the `RegisterModules` method to set up the `EventModule` and `UserModule`.
```
private static void RegisterModules(WebApplication app)  
{  
    app.UseEventModule();  
    app.UseUserModule();  
}
```

```
public static void ConfigureApplication(this WebApplication app)  
{  
    RegisterSwagger(app);  
    RegisterMiddleware(app);  
    RegisterModules(app);  
}
```

**Program.cs**:

```
var builder = WebApplication.CreateBuilder(args);  
builder.Services.RegisterApplicationServices();  
  
var app = builder.Build();  
app.ConfigureApplication();  
  
app.Run();  
```

In summary, the `SeedDatabase` method ensures that the `EventModule` database is in a consistent state during development. It drops and recreates the database to start fresh and adds sample data for testing or development purposes. By using this approach, we can easily reset the database to a known state whenever we start the application in a development environment. This is particularly useful for testing, debugging, and initial application setup.

# Notes:
## EnsureDatabaseDeletedAsync
Asynchronously ensures that the database for the context does not exist. 
	- If it does not exist, no action is taken. 
	- If it does exist then the **database is deleted**.  **Warning**: The entire database is deleted, and no effort is made to remove just the database objects that are used by the model for this context.

## EnsureCreatedAsync
- If the database exists and has any tables, then no action is taken.  It assumes that the database schema is already compatible with the Entity Framework model, and no changes or updates are required.
	- If the database exists but is empty (it doesn't have any tables), `EnsureCreatedAsync` comes into play. It uses the Entity Framework model to create the necessary tables and schema in the existing database. This means it will generate the tables, columns, and relationships defined in your Entity Framework model and apply them to the empty database.
	 - If the database does not exist at all, `EnsureCreatedAsync` not only creates the database but also uses the Entity Framework model to generate and apply the schema to the newly created database. This means it will create tables, columns, and relationships based on your Entity Framework model.
	It does not perform any migrations and only creates tables based on the relationships between your models. Hence, it is only suitable for test environments or development databases.