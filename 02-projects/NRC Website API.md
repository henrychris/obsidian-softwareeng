This [site](https://nrc.gsds.ng/).

It's extremely slow, makes repetitive requests and times out frequently. I'm led to believe the database is poorly designed and the code is poorly written. No caching or anything.

## Plan
- Analyse the responses returned on the booking area to understand the entities involved and design a proper database.
- Note what APIs would be required and plan their request and response bodies.
- Keep security in mind.

# Entities
1. Users
	- id
	- FirstName
	- LastName
	- PhoneNumber
	- Email
2. Stations
	- id
	- Name
	- Code
3. Trips
	- id
	- Name
	- VehicleName
	- VehicleCode
	- TripDate
	- FromStation, ToStation
		- stationId
		- sequence
		- arrivalTime
		- departureTime
		- distance
		- stationName
		- stationCode
	- Coaches
		- coachTypeId
		- coachTypeName
		- TravellerCategories
			- id
			- name
			- fareValue
		- availableSeats
		- unreservedSeats
		- unreservedSeatsStatus
4. TravellerCategory
	- id
	- Name
5. Coaches
	- id
	- coachName
	- coachNumber
	- availableSeatsCount
	- reservedSeatsCount
	- availableSeats 

Don't forget to allow payments using paystack.
A booking request contains the class, coach, passenger details per ticket, seating requirements and contact details.

