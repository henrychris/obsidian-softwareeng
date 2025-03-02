From [MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/What_is_a_progressive_web_app).

A PWA is a web app, that has the appearance of a platform specific application. They can be accessed from the web, are easily distributed, and can use standard web technologies. When installed on a platform, they can access more advanced Web APIs.

- They can run offline & in the background.
- They can use the whole screen.
- They have their own app icon on the home screen.

They are managed and ran by the browser engine. It interfaces between the application and the platform OS. 
Service workers are optional for PWAs, but are needed to provide an offline experience.

> We can use the [Background Sync API](https://developer.mozilla.org/en-US/docs/Web/API/Background_Synchronization_API) to send network requests as soon as a device goes offline. This can be used, or probably is used by Posthog to send analytics when the app is online.

## Progressive Enhancement
PWAs often use advanced APIs, some of which may not be supported by all browsers. In that scenario, the app should check if such a feature is available or not, and provide an acceptable fallback if it is not.
e.g., from MDN

For example, the [Background Sync API](https://developer.mozilla.org/en-US/docs/Web/API/Background_Synchronization_API) enables a PWA to ask a service worker to make a network request as soon as the device has connectivity. A classic use case for this is messaging. Suppose the user composes a message, but when the user tries to send the message, the device is offline. The Background Sync API enables the device to send the message in the background once the device is connected. On a device that does not support Background Sync, the app should let the user know the message could not be sent, giving them the chance to try again later.

## Making PWAs Installable
- They must have a manifest, linked using a HTML `<link>` tag. A manifest is a JSON file, defining the apps appearance or behaviour/
- It must be served through HTTPS or localhost
- If a browser determines that the app meets criteria, it will offer an option to install the app.
- We can customise the installation prompt to add themed UI, a description and screenshots. This doesn't work on iOS though (Fuck Apple).
- We can customise whether the PWA displays in the browser, or as platform app using the `display` element in the manifest.
	- If the browser does not support a given display mode, `display` will fall back to a supported display mode according to a predefined sequence. The [`display_override`](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest/Reference/display_override) enables you to redefine the fallback sequence.

## Offline & Background Operation
[Direct Link to MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Offline_and_background_operation)
### Service Workers
In a browser, web pages run a single thread (thanks Javascript). A service worker, the foundation of PWAs, is a web worker that runs in a separate thread and can communicate with the website thread by sending messages. It is created by the main thread by passing a URL to the worker's script.
The main app runs the HTML, CSS and JS implementing the app UI. The web worker handles background and offline tasks.

See: [Guide To Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers).

### Offline Operation
A service worker can fetch resources for an app it is connected to. When an app requests a resource, the browser fires a `fetch` request. This can be intercepted by the worker. We know browsers maintain a cache for webpages, and the service worker can add resources to this cache. The approach depends on the application, but usually there are two options:
- Cache-first
	- Try to get from cache
		- If success, return response
		- If fail, try to get from server
			- if success, clone and add to cache. return response.
			- if fail, try to return fallback response
				- if no fallback response, return *some* error response
- Network-first
	- try to fetch from server first, if failed, check cache, if failed check fallback, if failed return some error response
### Background Operation
Service workers can run in background while main app is closed. Of course, the browser can stop inactive workers if needed. But, if an event occurs that demands their attention, it will wake the worker.
This can be useful for background syncing, fetching, or pushing.
#### Sync
```js
// main.js

async function registerSync() {
  const swRegistration = await navigator.serviceWorker.ready;
  swRegistration.sync.register("send-message");
}
```

As soon as the application has network connectivity, the browser fires a `sync` event. To register the task, the main app gets the service worker, then registers a task with a `name`. When the event fires, the service worker checks for a task with the specified name, and runs the defined function.
```js
// service-worker.js

self.addEventListener("sync", (event) => {
  if (event.tag == "send-message") {
    event.waitUntil(sendMessage());
  }
});
```
`waitUntil` returns a Promise. This tells the browser not to kill the worker until the promise resolves. If it rejects, the browser may retry a few times. If the worker takes too long, it may be killed. 
How long is "too long" depends on the browser. For Chrome, the service worker is likely to be closed if:

- It has been idle for 30 seconds
- It has been running synchronous JavaScript for 30 seconds
- The promise passed to `waitUntil()` has taken more than 5 minutes to settle
#### Background Fetch
Sync is fine for short operations. Longer tasks will be stopped if we used sync, such as downloading a movie. With background fetch:
- The main app inits the request.
- Whether the main app is open or not, the browser displays a persistent UI element showing the progress and allowing users to cancel the request. Basically, the browser **takes over the network request/download**, managing it **separate from the main app**.
- When the request succeeds or fails, or the user has asked for a progress report, the browser wakes the service worker and fires the necessary event.
#### Periodic Background Sync
This allows an app to periodically update its data in the background while the main app is closed. The `periodicSync.register()` method accepts a minimum interval argument, defining the interval between sync attempts.
Note, the minimum interval specified by the PWA isn't what the browser will **give**. Apps used more often by the user are more likely to receive `periodicSync` events. 

When the browser decided to send a `periodicSync` event, it fires the event and the service worker calls the relevant handler in its `waitUntil` method.
If a PWA no longer needs `periodicSync` event, i.e when a user disables it, it can call `periodicSync.unregister()`.
#### Push
This allows the PWA to receive messages pushed by the server. When a message is received, the service worker is started, and a notification is displayed to the user.

Push messages aren't sent direct from app server -> device, instead they go from app server -> push service -> device. The messages should be encrypted and signed so the push service can't read them. 

For privacy reasons, the `push` permission is required for this API and the notifications **must** generate a notification visible to the user.

## Caching
Resources needed by the app are fetched using HTTP requests. PWAs can cache these resources, meaning they don't always need to be fetched by network requests. Of course, not all data should be cached. If the resource needs to be up to date, it probably shouldn't be cached.

Caching requires the `Fetch`, `Cache` and `ServiceWorker` APIs. Resources can be cached at different times:
- *The service worker's `install` event*: when the service worker is first downloaded and run, usually when the user first visits your site.
- *The service worker's `fetch` event*: fetch a request, cache the response or update the resource that's already in the cache.
- *In response to a user request*: A PWA might explicitly invite the user to download a resource to use later, when the device might be offline. If the file is large, the background fetch API will download the file, then the service worker will handle the response and save it to cache.
- *Periodically*: Using periodic sync, it can periodically fetch and cache responses.
## Best Practices
- Adapt to all browsers. Use [Feature Detection](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Testing/Feature_detection) to progressively enhance functionality. 
- Adapt to all devices: Use responsive design, and semantic HTML elements.
- Provide a custom offline experience: Let users know when they are using an offline version of your app.
- Offline operation: The app should support most of the apps function, even when offline. E.g. if an email is sent while offline, store the email and wait till the user goes online.
- Use deep links to support navigation, bookmarking and search engine indexing.
- Make the app **fast**: Users have greater expectations from installed apps, cause they are **offline**.
- Make it accessible.
- Provide an app like experience
	- Integrate with the platform OS
		- Display badges
		- Use platform APIs
		- Support [data sharing](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/How_to/Share_data_between_apps)
	- Look and Feel
		- Detect the users theme and apply it
		- Set an app icon
		- Use standalone `display` in your manifest
		- Use `system-ui` font-family
		- Use app-like UI elements, rather than web-UI, like headers and footers. 
See:
- [[What makes a good Progressive Web App](https://web.dev/articles/pwa-checklist)](https://web.dev/articles/pwa-checklist)
- [Best practices for PWAs](https://learn.microsoft.com/en-us/microsoft-edge/progressive-web-apps-chromium/how-to/best-practices)

## Icons
If you need to pick only one icon size, it should be 512 by 512 pixels. However, providing more sizes is recommended including 192 by 192, 384 by 384, and 1024 by 1024 pixel-sized images, too.
- 1024 x 1024
- 512 x 512
- 384 x 384
- 192 x 192