I've realised that I know nothing when it comes to auth. To remedy that, I'm reviewing all that I used to think.

## Misconception: JWTs are replacing cookies.
**JWTs** are an authentication mechanism. They are a means of encoding user data so that all necessary information is stored within the token. It is stateless, so any server in a cluster can process a request without storing session data.
It's very suited for API to API communication.

**Cookies** are small pieces of data stored in the users browser. They can store sessions, user settings or even be used for tracking. JWTs can also be stored in cookies. They are sent back to the server for later requests to maintain a **stateful** session - that is, they help the server know a request came from the same user.

	A cookie is a name value pair.
	Set-Cookie: my_cookie_name:my_cookie_value

Cookies can have two lifetimes: 
- **Permanent** - they are deleted on a date set by the `expires` or `max-age` attribute.
- **Session** - cookies without the attributes above are deleted when the current session ends. Some browsers restore sessions when they restart which can cause these to last indefinitely.

Always regenerate and resend session coolies when a user authenticates to prevent attackers from reusing user sessions.

Cookie access can be restricted with the following attributes:
- **HttpOnly** - can't be accessed with JavaScript's `Document.cookie` API, making it immune to XSS attacks.
- **Secure** - cookies are only sent in encrypted requests over HTTPs - except on localhost.

However, someone with access to the client's hard disk could access the data.

- **Domain** - specifies which server can receive a cookie. e.g. `Domain=google.com` means  `google.com` and subdomains like `developer.google.com` can receive the cookie.
- **SameSite** - specifies if the cookie can be sent with cross-site requests. 
	- `Strict` - only sends cookie with requests from the origin site - your website. Say you have a website that has *SameSite:Strict* cookies, `example.com`. If you visit it directly, the browser will check for cookies belonging to the domain, and append to the request. 
	  But, if you are on `external.com` and click a link making a request to `example.com`, even if the cookie exists, it won't be sent.
	- `Lax` - cookies will be sent when a user goes from an third-party site to the origin. If you are on `external.com` and make a request to `example.com`, any existing cookies will be sent along.

**Note For SameSite Attribute**
- The site is defined by domain AND scheme. `http://example.com` and `https://example.com` are treated as different sites.
- Using this attribute helps prevent Cross Site Scripting attacks where an attacked injects JS to run on your page.

**They both serve different purposes. One is for auth, the other is for storage.**


## Reality: Both are used together of late.
By storing a JWT in a cookie that is **HttpOnly**, **Secure** and **SameSite=strict**, you can get the advantages of both. Also include an *Anti-Forgery header.* Better still, using a Backend For Frontend, the cookie can be transformed to an auth header before it reaches the API.

Cookies can be easily deleted to log a user out. JWTs live for as long they are issued for.

**DON'T** store your JWT in local storage, store in a cookie.

Read: [[Common Attacks]]