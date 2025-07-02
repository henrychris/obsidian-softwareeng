---
share: "true"
---
**Default Exception Handler**:
1. This is an extension method for the `IApplicationBuilder` and is intended to be used in the startup configuration.
2. It uses the built-in `UseExceptionHandler` middleware to handle exceptions.
3. It is designed to provide a standard error handling response in case of exceptions and log the details using a provided or auto-resolved logger. For more on logging, refer to [[03-concepts/Logging - The Right Way]]. This is particularly relevant in a [[03-concepts/Modular Monolith]] where consistent error handling across modules is important.
4. The `logStructuredException` parameter allows you to log the exception details in a structured format.
5. It can capture the details of the exception and format them into a structured log message, which can be helpful for log analysis tools.

**Exception Middleware**:
1. This is a custom middleware class that you can add to the middleware pipeline in the startup configuration.
2. It explicitly catches exceptions within the middleware pipeline and provides custom handling for them.
3. It is useful when you need custom exception handling logic beyond the capabilities of the built-in `UseExceptionHandler`.
4. It provides a more manual and fine-grained control over how exceptions are handled and logged. For example, you can handle different exceptions in different ways.