### User Accounts
- [x] Enable users to create an account using *Google* login
  - [x] User email, username, profile picture, bio, social links
- [x] Allow users to update their profile information
### Venue Management
- [x] Allow users to create new venues
  - [x] Venue name, address, location coordinates, description, surface type
  - [ ] Ability to upload venue photos
- [x] Enable users to view a list of available venues
- [x] Allow users to edit existing venue details
- [x] Add & remove favourite venues
- [ ] Implement venue reviews
  - [ ] Users can leave reviews with star ratings and text
  - [ ] Reviews are associated with the specific venue
### Game Organisation
- [ ] Enable users to create new games
  - [ ] Game title, description, host, venue, date/time, entry fee, gender, player limit
- [ ] Display a list of upcoming games
- [ ] Allow users to join a game
  - [ ] Track players who have joined the game in the `GamePlayers` model
- [ ] Allow users to leave a game before it starts
  - [ ] Update the `GamePlayers` model accordingly
### Player Check-in
- [ ] Implement player check-in functionality
  - [ ] When a user arrives at a game, they can mark themselves as "checked in"
  - [ ] Update the `checkedIn` field in the `GamePlayers` model
### Additional Considerations
- [ ] Implement user notifications
  - [ ] Notify users of new games, game updates, cancellations, etc.
- [ ] Add search and filtering functionality
  - [ ] Allow users to search for venues, games, and other users
  - [ ] Filter games by location, date, player limit, etc.
- [ ] Introduce user roles and permissions
  - [ ] Define roles like "admin", "moderator", "regular user"
  - [ ] Manage access and abilities based on user roles