# 1. Core Game Management
- ~~Create team~~ 
- ~~Remove team~~
- Add team to match
- Remove team from match
- ~~Edit team~~
- Move team up in queue
- Move team down in queue
- Left side wins
- Right side wins
- Draw
- Create game
- Join game
- Create events
- Validate events
- See all connected users
- Design event payload
- Reconnect to game and get latest state
# 2. Real Time Updates
- Publish events
- Subscribe to events
- Render events
	- Consider sending heartbeats to sync state
- Implement a game log
# 3. Undo & Redo
- Design events with this in mind
- An undo/redo is a new event
# 4. Admin Management
- This is partially done in no. 1 when creating the game
- Handle admin reassignment on disconnect
	- If there are no users to reassign, wait for admin to reconnect
- Broadcast `ADMIN_CHANGE` events
- Show/hide admin specific controls
- Allow admins to transfer control to other users
# 5. Timer
- Implement `TIMER_START`, `TIMER_END`, `TIMER_PAUSED`, `TIMER_RESUMED` events.
- Sync new connection with admin timing
- Broadcast `TIMER_UPDATE` heartbeats
- Add frontend timer controls
	- Time is tracked locally and synced to admin
- Reset timers on `MATCH_STARTED`, `MATCH_ENDED` events.
# 6. Polish UI and Add Feedback Form
- consider using animations to highlight new events.