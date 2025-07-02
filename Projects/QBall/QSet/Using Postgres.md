If you’re implementing this system in **PostgreSQL**, you’ll need a normalized schema that leverages relational design principles while ensuring event immutability. Here’s a detailed schema design and query examples tailored to your use case.

---
## **PostgreSQL Schema Design**
### **1. Tables**
1. **Games**: Stores metadata and the latest state of the game.
2. **GameEvents**: Stores the immutable event log for all state changes.
3. **GameSnapshots** (optional): Stores periodic snapshots for efficient state recovery.
4. **Users**: Tracks users, their roles, and activity in the game.
---
### **1. `Games` Table**
Tracks high-level metadata and the current state of each game.
#### **Schema**
```sql
CREATE TABLE Games (
    gameId UUID PRIMARY KEY,          -- Unique identifier for each game
    createdAt TIMESTAMP DEFAULT NOW(),-- Game creation time
    adminUserToken TEXT NOT NULL,     -- Current admin token
    currentState JSONB,               -- Latest game state as JSONB
    lastEventId UUID,                 -- Pointer to the last event
    CONSTRAINT fk_lastEvent FOREIGN KEY (lastEventId) REFERENCES GameEvents(eventId)
);
```
#### **Example Record**
| gameId    | createdAt           | adminUserToken | currentState                             | lastEventId |
| --------- | ------------------- | -------------- | ---------------------------------------- | ----------- |
| `game123` | 2024-11-16 10:00:00 | `admin123`     | `{ "teams": [ ... ], "queue": [ ... ] }` | `event456`  |
#### **Common Use Cases**
1. **Fetch the latest game state**:
```sql
SELECT * FROM Games WHERE gameId = 'game123';
```
2. **Update the current state**:
```sql
UPDATE Games
SET currentState = $1, lastEventId = $2
WHERE gameId = 'game123';
```
---
### **2. `GameEvents` Table**
Stores an immutable log of all events, linked sequentially by `previousEventId`.
#### **Schema**
```sql
CREATE TABLE GameEvents (
    eventId UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- Unique identifier for the event
    gameId UUID NOT NULL,                              -- Foreign key to the game
    previousEventId UUID,                              -- Reference to the previous event
    eventType TEXT NOT NULL,                           -- Event type (e.g., ADD_TEAM, UNDO)
    eventPayload JSONB NOT NULL,                       -- Event-specific data
    timestamp TIMESTAMP DEFAULT NOW(),                 -- When the event was created
    CONSTRAINT fk_game FOREIGN KEY (gameId) REFERENCES Games(gameId),
    CONSTRAINT fk_previousEvent FOREIGN KEY (previousEventId) REFERENCES GameEvents(eventId)
);
```
#### **Example Records**
| eventId    | gameId    | previousEventId | eventType    | eventPayload                      | timestamp           |
| ---------- | --------- | --------------- | ------------ | --------------------------------- | ------------------- |
| `event123` | `game123` | `NULL`          | `GAME_START` | `{}`                              | 2024-11-16 10:00:00 |
| `event456` | `game123` | `event123`      | `ADD_TEAM`   | `{ "team": { "name": "Team A" }}` | 2024-11-16 10:01:00 |
#### **Common Use Cases**
1. **Replay all events for a game**:
```sql
SELECT * FROM GameEvents WHERE gameId = 'game123' ORDER BY timestamp ASC;
```
2. **Insert a new event**:
```sql
INSERT INTO GameEvents (gameId, previousEventId, eventType, eventPayload)
VALUES ('game123', 'event456', 'ADD_TEAM', '{"team": {"name": "Team B"}}');
```
3. **Fetch the latest event**:
```sql
SELECT * FROM GameEvents WHERE gameId = 'game123' ORDER BY timestamp DESC LIMIT 1;
```
---
### **3. `GameSnapshots` Table (Optional)**
Stores periodic snapshots of the game state for faster recovery.
#### **Schema**
```sql
CREATE TABLE GameSnapshots (
    snapshotId UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gameId UUID NOT NULL,
    eventId UUID NOT NULL,                 -- The event this snapshot corresponds to
    state JSONB NOT NULL,                  -- Full game state as of this snapshot
    timestamp TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_game FOREIGN KEY (gameId) REFERENCES Games(gameId),
    CONSTRAINT fk_event FOREIGN KEY (eventId) REFERENCES GameEvents(eventId)
);
```
#### **Example Records**
| snapshotId | gameId    | eventId    | state                                    | timestamp           |
| ---------- | --------- | ---------- | ---------------------------------------- | ------------------- |
| `snap123`  | `game123` | `event123` | `{ "teams": [ ... ], "queue": [ ... ] }` | 2024-11-16 10:20:00 |
#### **Common Use Cases**
1. **Retrieve the latest snapshot**:
```sql
SELECT * FROM GameSnapshots WHERE gameId = 'game123' ORDER BY timestamp DESC LIMIT 1;
```
2. **Recover state from the latest snapshot and replay events**:
 - Fetch snapshot:
```sql
SELECT * FROM GameSnapshots WHERE gameId = 'game123' ORDER BY timestamp DESC LIMIT 1;
```
 - Replay subsequent events:
```sql
SELECT * FROM GameEvents WHERE gameId = 'game123' AND timestamp > '2024-11-16 10:20:00' ORDER BY timestamp ASC;
```

---
### **4. `Users` Table**
Tracks user activity and roles in games.
#### **Schema**
```sql
CREATE TABLE Users (
    userToken TEXT PRIMARY KEY,             -- Unique token for each user
    lastSeenAt TIMESTAMP DEFAULT NOW(),     -- Last time the user was active
    role TEXT CHECK (role IN ('admin', 'guest')),
    gameId UUID NOT NULL,
    CONSTRAINT fk_game FOREIGN KEY (gameId) REFERENCES Games(gameId)
);
```
#### **Example Records**
| userToken  | lastSeenAt          | role    | gameId    |
| ---------- | ------------------- | ------- | --------- |
| `admin123` | 2024-11-16 10:15:00 | `admin` | `game123` |
| `user456`  | 2024-11-16 10:10:00 | `guest` | `game123` |
#### **Common Use Cases**
1. **Fetch a user's role in a game**:
```sql
SELECT role FROM Users WHERE userToken = 'admin123' AND gameId = 'game123';
```
2. **Update user activity**:
```sql
UPDATE Users SET lastSeenAt = NOW() WHERE userToken = 'admin123';
```
---
### **Common Queries for Your Application**
1. **Initialize a Client After Reconnection**:
 - Fetch the latest game state:
```sql
SELECT * FROM Games WHERE gameId = 'game123';
```
- Replay missed events:
```sql
SELECT * FROM GameEvents WHERE gameId = 'game123' AND timestamp > $lastSeenTimestamp ORDER BY timestamp ASC;
```
2. **Broadcast an Event**:
- Insert the event:
```sql
INSERT INTO GameEvents (gameId, previousEventId, eventType, eventPayload)
VALUES ('game123', 'event456', 'ADD_TEAM', '{"team": {"name": "Team C"}}');
```
   - Update the current state:
```sql
UPDATE Games
SET currentState = $newState, lastEventId = $newEventId
WHERE gameId = 'game123';
```
3. **Admin Reassignment**:
   - Find the longest-connected user:
```sql
SELECT userToken FROM Users WHERE gameId = 'game123' ORDER BY lastSeenAt ASC LIMIT 1;
```
   - Update the admin token:
```sql
UPDATE Games SET adminUserToken = $newAdminToken WHERE gameId = 'game123';
```
---
### **Key Advantages of Using PostgreSQL**
1. **Relational Integrity**:
   - Foreign keys and constraints ensure consistent relationships between `Games`, `GameEvents`, `GameSnapshots`, and `Users`.
2. **Query Power**:
   - PostgreSQL excels at aggregations and complex queries, making it easy to analyze events across games or track usage trends.
3. **JSONB Support**:
   - Flexible JSONB fields allow you to store semi-structured data (like current state or event payloads) without losing query capabilities.
4. **Performance with Indexing**:
   - Create indexes on frequently queried fields (e.g., `gameId`, `timestamp`, `eventType`) to speed up lookups.