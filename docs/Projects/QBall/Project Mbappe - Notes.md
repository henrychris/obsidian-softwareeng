# 13th November 2024
## Game Creation
Note the flow of 'Create Game' in the Footy Addicts application. 
- Choose a Venue
- Choose a Date and Time
- Provide Game settings:
	- Title
	- Description
	- Type: 5-a-side, 6-a-side, 7-a-side, 8-a-side, 9-a-side, 10-a-side, 11-a-side
	- Private or Public. Private is invite only.
	- Indoor (boolean)
	- Gender options: Men, Women, Mixed.
- Specify Payment:
	- Paid Online
		- Set price per player
		- Refund if the game is cancelled (boolean)
	- Cash
		- Set price per player
	- Free
## Venue Game Management
In real life, most venues have an existing game schedule, i.e they play on certain days at certain times. We want to keep the existing setup, not change it. Hosts, the users that create venues, should be able to manage games at their venues.
They can create games, update, or cancel them. They should also see games booked by users, and accept or reject them. This way they remain in control of bookings at their businesses.