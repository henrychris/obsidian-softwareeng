https://stackoverflow.com/questions/73117652/what-is-the-order-of-execution-of-the-same-type-hooks-in-fastify
https://github.com/fastify/fastify/blob/aa43e2de2cac18d7654c6a88e5437f8b0854872e/lib/hooks.js

if we add two of the same type of hook, they will be executed in the order they were added. monoscope's prehandler is registered in app.ts, so it will run before any prehandlers in routes. we don't have other onSend hooks, so it will be the only one.