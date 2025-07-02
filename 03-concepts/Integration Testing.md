---
share: "true"
---
Integration tests *test* the interaction between application components. They: 
- Use the actual components that the app uses in production.
- Require more code and data processing.
- Take longer to run.

Generally, you'd want limit the usage to critical features. You can write a set of read, write, update, and delete tests to verify the database connection though. And if you can write either a unit test or integration test for a function, choose the former.

**An example:**
In the [[../02-projects/Event Management API]], you can write a unit test for the ticket purchase system. A user would login, buy a ticket for an event, and receive the ticket. The event ticket count would be updated as well.

**Integration tests in ASP.NET Core require the following:**
- A test project is used to contain and execute the tests. The test project has a reference to the SUT.
- The test project creates a test web host for the SUT and uses a test server client to handle requests and responses with the SUT.
- A test runner is used to execute the tests and report the test results.


**Read or Watch:**
- [Integration tests in ASP.NET Core | Microsoft Learn](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-7.0)
- [Integration testing | ASP.NET Core 5 REST API Tutorial 15 - YouTube](https://www.youtube.com/watch?v=7roqteWLw4s)
- [Writing robust integration tests in .NET with WireMock.NET - YouTube](https://www.youtube.com/watch?v=YU3ohofu6UU&t=311s)
- [The Testing Technique Everyone Should Use in .NET - YouTube](https://www.youtube.com/watch?v=dasbRVz5MXo)
- [How To Reset Your Database when testing](https://www.youtube.com/watch?v=E4TeWBFzcCw&t=43s)
- [asp.net core - How to use WebApplicationFactory in .net6 (without speakable entry point) - Stack Overflow](https://stackoverflow.com/questions/69058176/how-to-use-webapplicationfactory-in-net6-without-speakable-entry-point)
- [ASP.NET Core Integration Tests Code Snippets](https://gist.github.com/Elfocrash/101ffc29947832545cdaebcb259c2f44)
- [C# - Using WebApplicationFactory in .Net 6 without startup (peterdaugaardrasmussen.com)](https://peterdaugaardrasmussen.com/2022/02/05/how-to-make-integration-tests-in-net-6-without-a-startup-cs-file/)

## IntegrationTest.cs
This is the base class inherited by all integration tests. Here is the most important section:

```
protected HttpClient TestClient = null!;  
  
[SetUp]  
public void Setup()  
{  
    var webApplicationFactory = new WebApplicationFactory<Program>()  
        .WithWebHostBuilder(builder =>  
        {  
            builder.ConfigureServices(services =>  
            {  
                // remove dataContext   
				var descriptorsToRemove = services.Where(  
                    d => d.ServiceType == typeof(DbContextOptions<EventDbContext>)  
                         || d.ServiceType == typeof(DbContextOptions<UserDbContext>)).ToList();  
  
                foreach (var descriptor in descriptorsToRemove)  
                {                    
	                services.Remove(descriptor);  
                }  
                
                // replace dataContext with in-memory versions  
			    services.AddDbContext<EventDbContext>(options => {
			    options.UseInMemoryDatabase("TestEventDB"); });  
            
	            services.AddDbContext<UserDbContext>(options => { 
	            options.UseInMemoryDatabase("TestUserDB"); });  
	            });        
		    });    
            
            TestClient = webApplicationFactory.CreateClient();  
}
```

We use `WebApplicationFactory<Program>` to create an *in-memory server* for our application, which we can use to send requests to various endpoints. To make this work, we added a partial class to our Program.cs file.

```
public partial class Program { // empty lol }
```

In the ConfigureServices section, we remove the actual database context configurations, preventing the tests from accidentally interacting with a real database. Then, we replace them with in-memory db configurations. 
Finally, the httpClient, `TestClient`, is created and can be used to make requests.

This is done in a Setup function so each test receives a fresh implementation. However, due to the [[DB Seeding]] setup defined here, seeding is also done for **every** test. That can be improved.
## Tests.cs
The test class inherits `IntegrationTest.cs` and writing tests is business as usual:

```
[Test]  
public async Task GetEvent_ShouldReturnUnauthorized_WhenAccessTokenIsMissing()  
{  
    const string id = "cecb7257-6764-4a5c-a9f8-6412d158214a";  
    var response = await TestClient.GetAsync($"/Events/{id}");  
  
    response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);  
}
```

[Fluent Assertions](https://fluentassertions.com/) is used to assert the test results.

Some tests require authorization:
```
protected async Task AuthenticateAsync()  
{  
    TestClient.DefaultRequestHeaders.Authorization =  
        new AuthenticationHeaderValue("bearer", await GetJwtAsync());  
}  
  
private async Task<string> GetJwtAsync()  
{  
    var registerResponse = await TestClient.PostAsJsonAsync("/Auth/Register",  
        new RegisterRequest("test", "user", "test1@example.com", "Password12@", "User"));  
  
    var result = await registerResponse.Content.ReadFromJsonAsync<ApiResponse<UserAuthResponse>>();  
    return result?.Data?.AccessToken ?? throw new InvalidOperationException("Registration failed.");  
}
```


Test:
```
[Test]  
public async Task GetEvent_ShouldReturnEvent_WhenEventExistsInDb()  
{  
    // Arrange  
    await AuthenticateAsync();  
   
    // Act  
    var createdEvent = await CreateEventAsync(new CreateEventRequest("Test Event",  
        "This is a test event", 10.99m,  
        DateTime.UtcNow.AddDays(7), DateTime.UtcNow.AddDays(7).AddHours(1),  
        DateTime.UtcNow.AddDays(7).AddHours(3)));  
  
    var response = await TestClient.GetAsync($"/Events/{createdEvent.Guid}");  
  
    // Assert  
    response.StatusCode.Should().Be(HttpStatusCode.OK);  
    var returnedEvent = await response.Content.ReadFromJsonAsync<ApiResponse<EventResponse>>();  
    returnedEvent?.Data?.Guid.Should().Be(createdEvent.Guid);  
    returnedEvent?.Data?.Name.Should().Be(createdEvent.Name);  
}
```

# Note
We should not test all behaviours with an integration test, that is obvious. As such, a rule of thumb should be:
- **Only write integration tests for methods that interact with the DB, or filesystem or external services**