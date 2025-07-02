# Auth
- Setup Identity
    - Add Roles: CommunityManager, Resident, SuperAdmin DONE
    - Add custom user class with these props: firstName, lastName, emailAddress, & isVerified DONE
    - add converter to store dates as UTC DONE
- Sign up
    - Create auth controller
    - Add endpoint to signup
    - Create signup request
        - Allow 'role' to be passed
        - Add validation
        - Handle request and save user to db
        - Consider email verification process
- Log in
    - Add endpoint to login
    - Create login request
        - Add validation
        - Generate JWT
        - Generate refresh token
        - Return user details on login
        - Consider implementing multi-factor authentication
- Refresh token
    - Add endpoint to refresh JWT
    - Create refresh token request
        - Add validation
        - Accept old jwt and refresh token
        - Invalidate old refresh token and issue new one
- Logout
    - Add endpoint to logout
    - Invalidate refresh token on logout
- Password reset
    - Add endpoints for requesting password reset and setting new password
- Account management
    - Add endpoints for updating user profile, changing password

# Community CRUD
- Create community controller
- Create Communities
    - Add endpoint to create community
    - Only community manager should have access to endpoint
    - Add validation
    - Return community details, date created and community manager name
- Get all communities created by a community manager
    - Add currentUser service to get data from HTTP context
- Get a community by id
    - Add endpoint
    - Accept userId to only get communities a user has access to
- Update a community
    - Add endpoint 
    - Check for better ways to handle updates
    - Consider using DTOs for update requests
- Delete a community
    - Add endpoint with proper authorization checks
- List communities
    - Add pagination and filtering options

# Add MassTransit with RabbitMQ 
- Install MassTransit NuGet packages
- Setup connection to RabbitMQ container with basic configuration
- Configure message consumers
- Implement retry policies and error handling

# Invite Resident To Communities
- This should be in community controller
- Call it InviteResidentToCommunityRequest
- Accept user email address & community id
- Create invite token for this user & email address
- Only one invite may be issued for an email address at a time
	- add hangfire to queue job to invalidate / mark a token as expired
    - If an invite has been created and is yet to expire, use that token
    - Send an email to that user, inviting them to signup
- Invite tokens should only last a week
- Publish event 
    - This event will send an email to the provided email address
- Consider bulk invite feature for multiple residents

# Join Community as Resident
- Provide invite token
- Check that invite token exists and is yet to expire
- Sign up user & add them to the community
    - Create community members table
    - Store communityId, userId & role (or roleId?)
- Publish an event
    - This event will notify the community manager
    - Add a community notifications table
- Consider allowing users to be part of multiple communities

# Send Emails
- Add email service using SMTP
    - Get implementation from Klusterthon project
- Implement email templates for different types of notifications
- Consider using a third-party email service for better deliverability

# Additional Considerations
- Implement logging and monitoring
- Add unit and integration tests
- Set up CI/CD pipeline
- Implement rate limiting for API endpoints
- Add Swagger/OpenAPI documentation
- Implement data validation and sanitization
- Consider adding WebSocket support for real-time notifications
- Implement caching strategy (e.g., Redis) for frequently accessed data
- Add user activity tracking and analytics
- Implement proper error handling and custom exception middleware