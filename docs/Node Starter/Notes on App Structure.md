The application entry point is app.js, most times. This is where middleware, routes, error handling & database connections are set up.

Routes are configured in a `/routes` directory. Usually, it is a file per group of routes. The routes are exported and configured in app.js with their base 'route'.
```js
// route file - catalog.js
const express = require("express");
const router = express.Router();
const book_controller = require("../controllers/bookController");

router.get("/", book_controller.index);

module.exports = router;
```

```js
// app.js
const catalogRouter = require("./routes/catalog.js");

app.use("/catalog", catalogRouter)
```

Unlike .NET where controllers are minimal, and services or 'slices' handle the request, the controller in the project I am building handles the request while the router simply calls the controller method.
```js
// bookController.js

exports.index = asyncHandler(async (req, res, next) => {
    res.send("NOT IMPLEMENTED: Site Home Page");
});
```

This can be changed as I learn more. Meanwhile, I need to check out VSA in JavaScript.
