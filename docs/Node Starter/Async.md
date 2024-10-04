Node is single-threaded. All events are handled on a single thread. This means that any long-running synchronous operations will block your application from handling other requests.
```js
setTimeout(function () {
  console.log("First");
}, 3000);
console.log("Second");

// 'Second' is logged immedidately, because control is returned.
// 'First' is logged after three seconds.
```
Above, the `setTimeout` function immediately returns control to the caller. When the timer runs out, it calls the provided 'callback function'. This is the most common way to avoid blocking in Node. There are other options like `async/await` or `Promises`.
## Promises
[MDN Docs](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous/Promises)
```js
async function myFunction {
  // ...
  await someObject.methodThatReturnsPromise();
  // ...
  await aFunctionThatReturnsPromise();
  // ...
}

try {
  // ...
  await myFunction();
  // ...
} catch (e) {
 // error handling code
}
```

In the code above, when `await someObject.methodThatReturnsPromise();` is hit, the execution of the entire function, `myFunction`, is paused until the async method returns. Once the method completes and returns, `myFunction` resumes operation.
This doesn't block the thread and other functions are free to run in the meantime.

Of course, we must await `myFunction()`, if not the try block won't catch any errors it throws.

When a method returns a Promise, and is called without awaiting, like:
```js
someObject.returnPromiseAsync();
```
It immediately returns a Promise. This includes info about it's current state, even though the operation isn't completed at the time. 
By using handlers, we can handle the eventual result of the promise.
```js
someObject.returnPromiseAsync()
.then((res) => console.log(res));
```

The `then()` call returns a promise as well, so we could chain these into perpetuity. I don't really like the approach though, and would prefer to use async/await.

To catch errors, we add a `catch` method at the end of our chain. This will be called if any part of the chain throws an error.
```js
someObject.returnPromiseAsync()
.then((res) => console.log(res))
.catch((error) => console.error(error));
```

If we need to write code where they can run in parallel, we can use `Promise.all()`.
```js
Promise.all([fetchPromise1, fetchPromise2, fetchPromise3])
  .then((responses) => {
    for (const response of responses) {
      console.log(`${response.url}: ${response.status}`);
    }
  })
  .catch((error) => {
    console.error(`Failed to fetch: ${error}`);
  });
```
It accepts an array of promises and returns a single promise. If there is any failure, the catch block immediately handles it. If all the operations succeed, it returns a `fulfilled` promise.
Of course, we could use `await` for this, and it would work fine.
```js
try {
	await Promise.all([fetchPromise1, fetchPromise2, fetchPromise3]);
} catch (error) {
	console.error(error);
}
```

If we don't need *all* the operations to succeed, we can use `Promise.any()`. This returns a fulfilled Promise if any of the operations succeed. If all operations fail, a rejected Promise is returned, with an `AggregateError`.
