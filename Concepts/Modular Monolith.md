---
share: "true"
---
### Modular Monolith
There were a lot of twists and turns, but I've finally got a hang of the setup. In the future, you can refer to [this](https://www.youtube.com/watch?v=l8fYpchrv0c&list=PLqqD43D6Mqz1QLbHRgQ-poMpBpJ4lYi42&index=6)) for advice.
There are four modules in my solution at the moment:
1. **API** - The entry point that collates and runs the other solutions.
2. **EventModule** - Responsible for all event related services.
3. **UserModule** - Responsible for authentication and user management.
4. **Shared** -  a shared library containing common entities and data.

#### Program.cs in API
```
builder.Services.AddControllers();
builder.Services.AddEventModule();
builder.Services.AddUserModule();
```
The application configures various services and components to be used within the container. These services include controllers, modules (e.g., `EventModule` and `UserModule`), and other dependencies required for handling HTTP requests and responses. AddEventModule and AddUserModule will be explained later.

```
var secrets = new ConfigurationBuilder()
    .AddUserSecrets<Program>()
    .Build();
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(
    x =>
    {
        x.TokenValidationParameters = new TokenValidationParameters
        {
            ValidAudience = secrets["JwtSettings:Audience"],
            ValidIssuer = secrets["JwtSettings:Issuer"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secrets["JwtSettings:Key"] ??
                throw new InvalidOperationException("Security Key is null!")),
            ValidateAudience = true,
            ValidateIssuer = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true
        };
    });
builder.Services.AddAuthorization();
```
The application configures authentication and authorization. It specifies the authentication scheme as JwtBearer, sets up token validation parameters, and includes authorization services. It also retrieves security-related settings and secrets from configuration files(as explained in [[#Dotnet Secrets]]).

```
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.UseEventModule();
app.UseUserModule();
app.UseMiddleware<ExceptionMiddleware>();
```

This section configures the middleware components that handle HTTP requests and responses:
- If the application is in the development environment, Swagger documentation and Swagger UI are enabled.
- `app.UseHttpsRedirection()` ensures that HTTP requests are redirected to HTTPS for secure communication.
- `app.UseAuthentication()` and `app.UseAuthorization()` add authentication and authorization middleware.
- `app.MapControllers()` maps routes and actions for controllers in the application.
- Custom modules, such as `EventModule` and `UserModule`, are configured using `app.UseEventModule()` and `app.UseUserModule()`.
- `app.UseMiddleware<ExceptionMiddleware>()` adds custom exception handling middleware to manage exceptions during request processing.

#### AddEventModule and AddUserModule
They both have similar structures:

```
public static IServiceCollection AddEventModule(this IServiceCollection services)  
{  
    services.AddCore();  
    return services;  
}  
  
public static IApplicationBuilder UseEventModule(this IApplicationBuilder app)  
{  
    return app;  
}
```

AddCore *adds* the services specific to that service. For EventModule:

```
internal static IServiceCollection AddCore(this IServiceCollection services)  
{  
    services.AddScoped<IEventService, EventService>();  
    services.AddAutoMapper(typeof(EventMappingProfile));  
    services.AddDatabase();  
    return services;  
}  
  
private static IServiceCollection AddDatabase(this IServiceCollection services)  
{  
    var config = new ConfigurationBuilder()  
        .AddJsonFile("appsettings.json", optional: false)  
        .Build();  
    services.AddDbContext<EventDbContext>(options =>  
        options.UseSqlite(config["ConnectionStrings:EventConnection"]));  
    return services;  
}
```

#### Conclusion
I set EventModule, UserModule and shared as class libraries. API is the startup project.
