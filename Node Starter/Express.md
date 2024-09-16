```js
// import and create express app
const express = require("express");
const app = express();

// add a route handler
app.get("/", function (req, res) {
    res.send("Hello World!");
});

// start the server
app.listen(port, function () {
    console.log(`Example app listening on port ${port}!`);
});
```

## Routes
We can group routes together, similar to 'controllers' in .NET. This requires the express `Router`.
```js
const express = require("express");
const router = express.Router();

// home page
router.get("/", function (req, res) {
    res.send("Home page!");
});

// about page
router.get("/about", function (req, res) {
    res.send("About page!");
});

// export the entire class
module.exports = router;
```

Then, we import and use the router in the `index.js` file:
```js
const wiki = require("./routes/wiki.js");

app.use("/wiki", wiki);
```

We can also get path parameters like so:
```js
router.get("/:userId", function (req, res) {
    res.send(req.params.userId);
});
```

See more [here](https://expressjs.com/en/guide/routing.html).
## Middleware
Express supports middleware. You can either [create](https://expressjs.com/en/guide/writing-middleware.html) or [use](https://expressjs.com/en/guide/using-middleware.html) existing middleware.
```js
const logger = require("morgan");

app.use(logger("dev"));

// you can also apply middleware to specific routes
app.use("/wiki/about", logger("dev"));
```

The `express.static()` middleware is inbuilt and used to server static files from a specific folder. The files are served relative to their directory on the server.
```js
// serves files from the public folder.
app.use(express.static("public"))
```
You can call `static()` multiple times to serve multiple directories. If a file cannot be found by one middleware function then it will be passed on to the subsequent middleware.

Note that with all middleware, the order is important. Middleware are called in the order they are registered.

You can also create a virtual prefix for your static URLs. Instead of using the folder they are stored at in the URL, it uses the prefix.
```js
app.use("/media", express.static("public"));

// files can be fetched from /media/js/whatever
```

# Express Generator
```bash
npm install express-generator -g

express [directory-name] --view=pug # use the pug templating engine

# and that's it
```

See more [here](https://expressjs.com/en/starter/generator.html).