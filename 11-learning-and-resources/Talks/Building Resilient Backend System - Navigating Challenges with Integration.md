**Speaker:** Anthony Alaribe

# Common API Challenges
- Sandbox and Production environments are different and have different endpoints
- New request fields are missing from documentation
- No changelogs to track change history 

# Performance Challenges
- Latency problems
- Rate limiting
- Inefficient Data handling
- Timeouts != request failure
	- **TODO:** How do we use CancellationToken to allow requests to be cancelled?

# Reliability Concerns
- Poor error responses
- Inconsistent error behaviour: Different error formats
	- e.g : Mixing snake and camel case, different versioning practices, different auth practices
	- **TODO:** We should use a consistent message for internal server errors.

# Security Risks
- DDOS attacks
- Unvalidated inputs
- Unauthorised access & incorrect auth configuration

# Best Practices
- Log all request payloads
- Log all response payloads
- Test in *Production*.
- Automate documentation updates.
	- Figure out how to generate documentation from code.
- Use tools to block malicious actors & DDOS attacks
- Lint your APIs to spot injection attacks
- Check out OWASP top 10
- Avoid weak JWT configurations
- Use expected HTTP patterns, like 429 when rate limiting