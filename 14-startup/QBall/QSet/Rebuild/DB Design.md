**Session**
- id (uuid)
- displayName (varchar)
- status (enum: Active, Ended & Archived)
- teams \[ \] (Team collection)
- matches \[ \] (Match collection)
- queueEntries \[ \] (QueueEntry collection)
- createdAt (datetime)
- updatedAt (datetime)

**Team**
- id (uuid)
- name (varchar)
- sessionId (uuid, **FK**)
- wins (int)
- losses (int)
- draws (int)
- matches \[ \] (Match collection)
- currentStreak (int)
- createdAt (datetime)
- updatedAt (datetime)

**Match**
- id (uuid)
- sessionId (uuid, **FK**)
- teamAId (uuid, **FK**)
- teamBId (uuid, **FK**)
- result (nullable enum: TeamAWin, TeamBWin or Draw)
- matchEvents \[ \] (MatchEvent collection)
- createdAt (datetime)
- completedAt (datetime)

**QueueEntry**
- id (uuid)
- sessionId (uuid, **FK**)
- teamId (uuid, **FK**)
- position (int)
- createdAt (datetime)
- updatedAt (datetime)