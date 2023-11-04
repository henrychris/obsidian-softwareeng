### Authentication v Authorization
- Authentication involves verifying the identity of a user, aka, "Who are you?" It involves verifying the credentials provided by a user or entity to confirm their identity.
- Authorisation is concerned with determining the actions a verified user or entity can perform on a system, aka "What are you allowed to do?" It defines what resources they can access or the permissions and privileges granted to them.

This used to be done using sessions. 
#### Session
- User login credentials are verified. If correct, the user is stored in the session (which is stored in server memory), and they receive a unique ID - a session ID. 
- The session ID is sent back as a cookie. For every request, the session ID and cookie are sent to the server.
- The server checks the session in memory for a  session ID and fetches the user. 
- The user is verified to see that they have authorisation to access that resource. If they do, a response is sent back with the data.

#### JWT
- User login credentials are verified. If correct, a JWT is generated for the user, encodes and signs it with a secret key. If it is tampered with, the server can recognise that and refuse access.
- The JWT is sent to the client.
- Every request is sent to the server including the JWT. The server verifies the JWT signature (also checks the token is unchanged) and gets the user from the JWT.
- If the user is authorised to access the resource, the response is sent back.

**The main difference**: Sessions store the user info on the server, and JWTs store the info in the token which is stored on the client. 
JWTs are stateless as the server doesn't have to remember anything.
