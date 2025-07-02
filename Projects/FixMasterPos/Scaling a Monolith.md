# Caching
- For infrequently changing data
- Reduces workload on DB
- L1 Cache? The smallest cache in a multi-cache system.
# Database Indexing

# Query Efficiency
- Only fetch what is needed in requests. 
# Observability and Monitoring
- Measuring Slow Endpoints
	- Log every action in a request. 
	- Check the time between each action in the request
	- Cut out the fat.
- PM2
- Cloudwatch
- Sentry
- GroundCover
# Sharding and Replication
# Background Jobs and Async Processing
- Sending emails
- Large file manipulation
- Imports and Exports
# Testing
- Create Tests on Postman
- Use these to test endpoint functionality
	- Speak with QA to get test cases
# Database and Server Locations
- We should check that our systems are co-located. If DB and server are on different sides of the world, that adds a latency cost to every request.

https://fintektime.wordpress.com/2017/04/21/scalability-for-dummies/

# Day By Day
## Day 1 - June 5th
### Get All Customers
![[Pasted image 20250610172220.png]]
The existing code had a classic N+1 query:
1. Fetch all customers with filters (1 query)
2. For each customer, make 2 additional queries:
- Count their total orders
- Fetch all their order details for aggregation
This meant 200+ database queries for just 100 customers.
#### Solution
- Replaced the N+1 pattern with a single MongoDB aggregation pipeline
- Added necessary database indexes
- Removed unnecessary data from the response
#### Results 
From 200+ queries → 1 aggregation query
P90 response time now under 1.6 seconds
#### Takeaway
As I mentioned, the issues are mainly database query patterns, not infrastructure. But I still intend to add a caching layer in front of this endpoint (and others, where needed).
## Day 2 - June 6th
