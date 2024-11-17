# Models
## Venue
- Name
- Address
- Location Coordinates
- Description
- Surface Type
- Reviews \[ \]
- Games \[ \]
- PhotoUrls \[ \]
- DateCreated
- DateUpdated
## Review
- Reviewer
- Stars
- Review Text
- DateCreated
- DateUpdated
## Game
- Title
- Description
- Host
- Venue
- DateTime
- EntryFee
- Gender
- PlayerLimit
- PlayersJoined
- Status
- DateCreated
- DateUpdated
## GamePlayers
- GameId
- UserId
- CheckedIn
- DateCreated
- DateUpdated
## User
- Email
- Username
- ProfilePictureUrl
- Bio
- SocialLinks
	- Twitter?
	- Instagram?
- DateCreated
- DateUpdated
# Features
## Venue Management
**Models Involved**: `Venue`, `Review`, `Users`.
The `Venue` model represents the physical locations where games can be played. Users can search for and browse available venues based on location, surface type, and other attributes. The `Review` model allows users to leave feedback and ratings on the venues they've used. Users create venues.

**Relationship**: A `Venue` can have multiple `Review` records associated with it, as users share their experiences at that location.
## Game Organisation
**Models Involved**: `Game`, `GamePlayers`, `User`
The `Game` model represents the individual football (or other sport) matches that users can join. Each game is associated with a `Venue` and a `Host` user. The `GamePlayers` model tracks the users who have joined a specific game, as well as their check-in status.

**Relationships**: A `Game` has a one-to-many relationship with `GamePlayers`, and a `GamePlayers` record has a many-to-one relationship with both `Game` and `User`.
## User Profiles
**Models Involved**: `User`
The `User` model stores the personal information, sports experience, and social media links for each registered user. This allows users to build a profile and connect with others who share similar interests and skill levels.

**Relationships**: The `User` model does not have any direct relationships with the other models, but its data is leveraged throughout the application, such as for creating venues, hosting games, joining games, and leaving reviews.
# Key Features
1. **Venue Discovery**: Users can browse and search for available venues based on location, surface type, and other criteria. They can also leave reviews for venues they've used.
2. **Game Creation and Joining**: Users can create new games at a selected venue, specifying details like date/time, entry fee, and player limit. Other users can then join these games.
3. **Player Check-in and Attendance Tracking**: When users arrive at a game, they can check in, and the `GamePlayers` model tracks their attendance.
4. **User Profiles and Connections**: Users can build out their profiles, showcasing their sports experience and interests. This helps other users find suitable game partners and hosts.