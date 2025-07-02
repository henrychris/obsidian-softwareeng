---
share: "true"
---

Alright. The aim is to build a monolithic API with separated application layers so that it can easily be deployed using Microservices architecture, for the sake of it.

Refer to these:
- [How to recover from microservices (hey.com)](https://world.hey.com/dhh/how-to-recover-from-microservices-ce3803cc)
- [Lee Atchison | Moving Beyond the Microservices Hype](https://leeatchison.com/app-architectures/moving-beyond-microservices-hype/)
- [Death by a thousand microservices (renegadeotter.com)](https://renegadeotter.com/2023/09/10/death-by-a-thousand-microservices.html)
- [Build the modular monolith first (fearofoblivion.com)](https://www.fearofoblivion.com/build-a-modular-monolith-first)
- [Event API Tasks](https://mammoth-moth-7a3.notion.site/9a64b7776e554ebbb6e4f59dfd453f0d?v=770cd4ce555b473295a789749e743716&pvs=4)
- [MVC Testing Framework]

Related Concepts:
- [[Default Exception Handler vs Exception Middleware]]
- [[Authentication v Authorization]]
- [[../03-concepts/Modular Monolith]]
- [[Microsoft.NET.Sdk.Web v Microsoft.NET.Sdk]]
- [[Dotnet Configuration - Secrets]]
- [[Records vs Classes]]
- [[Repository Pattern and Unit of Work]]
- [[Using Docker for SQLServer in .NET]]
- [[../03-concepts/Integration Testing]]

## Notes

### Adding Identity to an API
- MS Identity adds cookies by default. In an API, we'd prefer to use JWT tokens instead.

### API "Language" Translation
- Most of the time, an API converts a DTO to the internal "language" of the system, then performs some application logic, and maps the response to a DTO to match the external language. AutoMapper does all that messy shit for me.

### Operations and Status Codes
- **UPDATE** using ***HTTP PUT***: If an existing resource is updated, return a 200 or 204. If a new resource is created, return 201.
- **DELETE** using ***HTTP DELETE***: If an existing resource is deleted, return 200. If the resource didn't exist in the first place, return 204. You can also return a 204 by default if you don't want to send any data.
- **GET** using ***HTTP GET***: return a 404 if the resource doesn't exist, else, return 200.
- **CREATE** using ***HTTP POST***:  A 201 is a fitting response and should contain a location header that directs to the location of said resource, such as the endpoint to fetch the data from. A 200 can be sent if no accessible resource is created, e.g., if we are only sending an access token.

Read: [Which HTTP Status Code to Use for Every CRUD App | Moesif Blog](https://www.moesif.com/blog/technical/api-design/Which-HTTP-Status-Code-To-Use-For-Every-CRUD-App/)

### Controller Response Handling
I have decided to use this structure for all API responses:
```
{
"status": "[boolean]",
"message": "[string]",
"data": "[object]"
}
```

For success, it is straightforward - wrap response in the relevant statusCode and send to the client. For failures, we need to get the exact failure and its statusCode as well as the list of errors.

So, we will fetch the list of errors. Determine the status code, and return an ObjectResult. 

### Implementing JWTs and MS Identity
1. Create your user entity and DbContext. You can decide to use the default IdentityUser and IdentityRole, but you can also customise it if you need to.
```
// inherit from IdentityUser 
public class ApplicationUser : IdentityUser{}

// inherit from IdentityDbContext and create a constructor
public class UserDbContext : IdentityDbContext<ApplicationUser>  
{  
    public UserDbContext(DbContextOptions<UserDbContext> options) : base(options)  
    {    }
}

// call AddIdentity in Startup or Program.cs
services.AddIdentity<ApplicationUser, IdentityRole>(// options )
.AddEntityFrameworkStores<UserDbContext>()  
.AddDefaultTokenProviders();
```

2. Add authentication and set default authentication schemes. The scheme **must** be set, so the appropriate challenge is used to authenticate the user. Else, it would try to redirect to the login endpoint.
```
builder.Services.AddAuthentication(options =>  
    {  
        options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;  
        options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;  
        options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;  
    }).AddJwtBearer(// options);

// add JwtBearer settings as suitable

.AddJwtBearer(  
    x =>  
    {  
        x.TokenValidationParameters = new TokenValidationParameters  
        {  
            ValidAudience = secrets["JwtSettings:Audience"],  
            ValidIssuer = secrets["JwtSettings:Issuer"],  
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secrets["JwtSettings:Key"] ??  
                throw new InvalidOperationException("Security Key is null!"))),  
            ValidateAudience = true,  
            ValidateIssuer = true,  
            ValidateLifetime = true,  
            ValidateIssuerSigningKey = true,

			// this is important for RBAC to work.
            RoleClaimType = JwtClaims.Role  
        };  
    });
```

3. Remember to add:
```
// In this exact order.
app.UseHttpsRedirection();
app.UseAuthentication();  
app.UseAuthorization();
```

If using Identity, make sure to register identity BEFORE setting up JWT auth.
### Ticketing
Track the capacity of the event. On each sale, reduce the available no of tickets.
Add EventCapacity and TicketsSold. Add to TicketsSold as user's buy tickets. Use the difference between both to calculate TicketsAvailable on the frontend.

### Adding Google Sign-in
clientid: 662210794059-jmh1a5dnol6pj62l4g8h64a71i9n24em.apps.googleusercontent.com
client secret: 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
### TODO
- Work on features and stop faffing about.
- Add OrganiserId to event table
- Add message passing with a bus (rabbit MQ maybe)
- Look at ticket generation and email sending (update ticket purchase endpoint)
- Tickets can be a separate module tbh. Enter from the event and send a request? Overly complex for no reason though.
- Update README to mention database tools. Or, dockerise the application.
- State management for event status. The date should match the status.
- Implement API Security