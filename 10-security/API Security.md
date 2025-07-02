- Always use HTTPS
- Do NOT place sensitive data in query parameters
- Implement Rate Limiting to prevent brute-force attacks
	- Ban users that have too many server errors
	- Clear the X-Powered-By header
- Always ask for user credentials for **critical** actions, e.g change email
- Never use a GET query for a mutation. 

# Two Main Auth Mechanisms
- Bearer Token (See: [[10-security/Refresh Tokens]])
- Authentication Cookie

For a deeper understanding of the difference between authentication and authorization, refer to [[10-security/Authentication v Authorization]].
## Token Security
- Don't store token in local storage
- Store in HttpOnly, Secure cookie
## Cookie Security
- Use HttpOnly to mitigate XSS
- Use SameSite to mitigate CRSF, but, it's not available on all browsers
	- Short Session Timeouts
	- [[Double Submitted Cookies]]

# Combining Both Approaches

From Mobile -> Send Bearer Token