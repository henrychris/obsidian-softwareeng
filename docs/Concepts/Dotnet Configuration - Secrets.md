---
share: "true"
---
- ***Note***: These secrets are only registered in a development environment. For production scenarios, use other methods.
- Run this command:
```
dotnet secrets init
```
- Find the `secrets.json` file and add your *secrets*. A Secrets ID is added to the .csproj file, add it to all projects referencing the `secrets.json` file.
- Secrets are added to configuration by default. Simply inject IConfiguration to use them. However, if you need to access them in Program.cs or Startup.cs, use:
```
  var secrets = new ConfigurationBuilder()  
    .AddUserSecrets<Program>()  
    .Build();
```

Related: [.NET Configuration In Depth](https://youtu.be/aOXaBZFB0-0?list=TLPQMTcxMTIwMjOEFSQY1gqxhw)
