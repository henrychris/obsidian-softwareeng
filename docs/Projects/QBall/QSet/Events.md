```json
{
  "eventId": "unique-uuid",
  "eventType": "CREATE_TEAM",
  "eventPayload": {
    // Specific to the action (see below)
  },
  "gameId": "game-uuid",
  "userId": "user-uuid",
  "previousEventId": "previous-event-uuid",
  "timestamp": "2024-11-18T12:34:56.789Z",
  "currentGameState": {
    // The full current state of the game (see below)
  }
}
```
GameState
```json
"currentGameState": {
  "teamsInMatch": [
    {
      "teamId": "team-uuid-1",
      "teamName": "Team 1",
      "stats": {
        "wins": 2,
        "draws": 0,
        "losses": 1
      }
    },
    {
      "teamId": "team-uuid-2",
      "teamName": "Team 2",
      "stats": {
        "wins": 2,
        "draws": 1,
        "losses": 1
      }
    }
  ],
  "waitingTeams": [
    {
      "teamId": "team-uuid-3",
      "teamName": "Team 3",
      "stats": {
        "wins": 1,
        "draws": 0,
        "losses": 0
      }
    },
    {
      "teamId": "team-uuid-4",
      "teamName": "Team 4",
      "stats": {
        "wins": 1,
        "draws": 0,
        "losses": 0
      }
    }
  ]
}
```

Example
```json
{
  "eventId": "unique-uuid-4",
  "eventType": "LEFT_TEAM_WINS",
  "eventPayload": {
    "leftTeamId": "team-uuid-1",
    "rightTeamId": "team-uuid-2"
  },
  "gameId": "game-uuid-1",
  "userId": "user-uuid-admin",
  "previousEventId": "unique-uuid-3",
  "timestamp": "2024-11-18T12:20:00Z",
  "currentGameState": {
    "teamsInMatch": [
      {
        "teamId": "team-uuid-1",
        "teamName": "Team 1",
        "stats": {
          "wins": 3,
          "draws": 0,
          "losses": 1
        }
      },
      {
        "teamId": "team-uuid-3",
        "teamName": "Team 3",
        "stats": {
          "wins": 1,
          "draws": 0,
          "losses": 0
        }
      }
      }
    ],
    "waitingTeams": [
      {
        "teamId": "team-uuid-4",
        "teamName": "Team 4",
        "stats": {
          "wins": 1,
          "draws": 0,
          "losses": 0
        }
      },
      {
        "teamId": "team-uuid-2",
        "teamName": "Team 2",
        "stats": {
          "wins": 2,
          "draws": 1,
          "losses": 3
        }
    ]
  }
}
```