As far as I know, Fastify requires us to convert zod schema's to json. The json is passed to the route and used to validate the request.

Unfortunately, this prevents us from using more complicated validation & strips away any helpful error messages.

As an alternative, we can use middleware that runs on every request. The middleware will accept a zod schema, and validate the request according to the validation rules.
The error messages will be wrapped nicely and returned to the frontend in a useful format.
# Exception Middleware
We have no exception handler, and the client sees error messages. This should not happen.