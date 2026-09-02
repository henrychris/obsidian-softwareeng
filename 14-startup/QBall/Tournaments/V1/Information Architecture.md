# Routing Model
The tournament is the primary routing boundary for the host application.
## Host Routes

```text
/tournaments
/tournaments/new
/tournaments/:tournamentId
/tournaments/:tournamentId/matches
/tournaments/:tournamentId/matches/:matchId
/tournaments/:tournamentId/standings
/tournaments/:tournamentId/teams
/tournaments/:tournamentId/teams/:teamId
/tournaments/:tournamentId/players
/tournaments/:tournamentId/players/:playerId
/tournaments/:tournamentId/stats
/tournaments/:tournamentId/audit
/tournaments/:tournamentId/settings
/account
```

Host routes use the tournament's immutable internal ID.
## Public Routes
```text
/t/:slug
/t/:slug/matches/:matchId
/t/:slug/players/:playerId
```

Public routes use the tournament slug.

If the tournament name changes, the public slug remains the same. Host routes remain unchanged.

---
# Application-Level Navigation
Outside an individual tournament:
```text
My Tournaments
Create Tournament
Account
```
## My Tournaments
**Route**

```text
/tournaments
```

Shows tournaments owned by the current user.
## Create Tournament
**Route**
```text
/tournaments/new
```

Starts the tournament setup flow.
## Account
**Route**
```text
/account
```

Contains account and authentication-related information.

---
# Tournament Workspace Sidebar
Inside an individual tournament:
```text
Dashboard
Matches
Standings
Teams
Players
Stats
Audit Log
Settings
```

---
# Dashboard
**Route**
```text
/tournaments/:tournamentId
```
The dashboard is a summary and operational overview, not a replacement for the detailed sections.

It should answer:
- What is happening now?
- What is happening next?
- What needs attention?
## Information
### Tournament Header
- Tournament name
- Tournament status
- Publish status
- Public page link
- Primary contextual action

Possible primary actions:
- Pay ₦2,000
- Publish
- Complete Tournament
### Live Now
Shows all currently live matches.

Each match card may show:
- Teams
- Current score
- Match phase
- Link to match control

Multiple matches may be live simultaneously.
### Next Up
Shows the next few upcoming fixtures.
### Competition Preview
A compressed version of the tournament's current competition state.
#### Group Stage
Allow the host to switch between groups.

Show only:
```text
P
W
D
L
Pts
```

Do not show GF, GA, or GD on the dashboard.
#### Group + Knockout Tournament
Top-level switch:
```text
Groups | Knockout
```

While the group stage is active, default to Groups.
Once the knockout phase is active, default to Knockout.
Groups show compact standings.
Knockout shows a compact current-round/bracket preview.
#### Pure Knockout Tournament
Show the compact knockout preview directly.

Include a clear link to the full Standings page.
### Leaders
Compact leaderboard previews:
- Top scorer
- Top assists
- Top clean sheets
### Action Required
Examples:
- Missing lineups
- Postponed matches
- Tournament ready to complete
- Unpublished tournament
## Responsive Behaviour
Desktop may use a card/grid layout.
Mobile should use a single vertical feed ordered by operational importance.
Detailed data should link to its dedicated section rather than being reproduced in full.

---
# Matches
**Route**
```text
/tournaments/:tournamentId/matches
```
## Filters
```text
All
Live
Upcoming
Completed
Postponed
Cancelled
```
Cancelled fixtures remain visible to the host but are hidden publicly.
## Match List Information
- Teams
- Stage/group
- Match state
- Result
- Resolution type, when completed
- Assigned date/time, if any
## Actions
- Create match manually
- Rearrange fixtures
- Start match
- Enter result directly
- Set/edit lineup
- Postpone
- Reschedule
- Cancel
- Mark walkover

---
# Match Detail / Match Control
**Route**
```text
/tournaments/:tournamentId/matches/:matchId
```
## Information
- Teams
- Score
- Match state
- Match phase
- Formations
- Starting lineups
- Substitutes
- Event feed
- Goals
- Assists
- Own goals
- Yellow cards
- Red cards
- Substitutions
## Match Controls
- Start match
- End match
- Continue to extra time
- Continue to penalties
- Record event
- Edit/delete event
- Add late-arriving player to lineup
- Record substitution
- Complete match
- Correct completed match while edits are allowed

---
# Standings
**Route**
```text
/tournaments/:tournamentId/standings
```

The Standings page is the authoritative competition-state view.
## Group + Knockout Tournament
### Tier 1
```text
Groups | Knockout
```
The Knockout option is shown only when the tournament has a knockout phase.
### Groups
Second-level navigation:
```text
Group A | Group B | Group C | ...
```

Default to the first group.
Show the selected group's full table:
```text
P
W
D
L
GF
GA
GD
Pts
```
Also show:
- Qualification markers
- Group status
- Tiebreak context where relevant
### Knockout
Show the full knockout bracket.
## Pure Round Robin / Group Tournament
Show group/league selector where applicable, followed by the full table.
## Pure Knockout Tournament
Show the full bracket directly.

---
# Teams
**Route**
```text
/tournaments/:tournamentId/teams
```
## Team List
Show:
- Team logo
- Team name
- Jersey colour
- Captain
- Roster count
- Active / withdrawn status

Before the first match starts:
- Add team
- Remove team

After the first match starts:
- Team structure is locked
- Teams may only be withdrawn

---
# Team Detail
**Route**
```text
/tournaments/:tournamentId/teams/:teamId
```
## Information
- Team identity
- Logo
- Jersey colour
- Captain
- Roster
- Upcoming matches
- Results
- Team statistics
- Lineup history
- Withdrawal status

---
# Players
**Route**
```text
/tournaments/:tournamentId/players
```

Players are managed tournament-wide rather than exclusively inside teams.
## Filters
```text
All
By Team
Unassigned
Inactive
```
## Player List Information
- Photo
- Full name
- Known-as / nickname
- Position(s)
- Shirt number
- Current team
- Active / inactive status
- Summary stats
## Actions
- Add player
- Edit player
- Assign to team
- Reassign to team
- Remove from team
- Make inactive

Unassigned players remain available for match lineups.

---
# Player Detail
**Route**
```text
/tournaments/:tournamentId/players/:playerId
```
## Information
- Photo
- Full name
- Known-as / nickname
- Positions
- Shirt number
- Current team
- Active / inactive status
- Tournament statistics
- Teams represented
- Match history
- Goals
- Assists
- Own goals
- Cards
- Clean sheets
- Appearances
---
# Stats
**Route**
```text
/tournaments/:tournamentId/stats
```
## Top-Level Tabs
```text
Players | Teams | Awards
```
## Players
Leaderboards for:
- Goals
- Assists
- Clean sheets
- Yellow cards
- Red cards
- Own goals
- Appearances
## Teams
Statistics such as:
- Goals
- Clean sheets
- Cards
- Wins
- Draws
- Losses
## Awards
Display and manage:
- Champion
- Top scorer
- Top assists
- Most clean sheets
- Best goalkeeper
- Most yellow cards
- Most red cards
- MVP / Player of the Tournament

Awards may be shared where appropriate.
Manual awards such as MVP are selected by the host.

---
# Audit Log
**Route**
```text
/tournaments/:tournamentId/audit
```

The audit log is permanent and public-facing.
## Filters
```text
All
Matches
Teams
Players
Tournament
```
## Entries
Every meaningful mutation should be recorded.

Examples:
- Tournament details changed
- Fixture rescheduled
- Match result corrected
- Goal edited
- Card removed
- Team withdrawn
- Player reassigned
- Roster changed
- Lineup changed
- Tournament published/unpublished

Where possible, show:
```text
Before → After
```

Publicly, the actor is displayed as:
```text
Tournament Host
```

The backend stores the actual user responsible for the action.

---
# Settings
**Route**
```text
/tournaments/:tournamentId/settings
```
## General
- Tournament name
- Description
- Organiser name
- Logo/banner
- Venue
- Start date
## Competition
- Tournament format
- Team size
- Groups
- Fixture rounds
- Qualification rules

These settings become read-only once the first match starts.
## Publishing
- Public slug
- Preview public page
- Publish
- Unpublish
## Tournament
- Tournament status
- Complete tournament
- Delete tournament

---
# Public Tournament Information Architecture
**Route**
```text
/t/:slug
```

The public page is spectator-focused and read-only.

It exposes:
- Overview
- Live Now
- Fixtures / Results
- Standings / Groups / Bracket
- Teams
- Players
- Stats
- Awards
- Audit Log

All live competition information updates in real time.

---
# Public Match Page
**Route**
```text
/t/:slug/matches/:matchId
```
Shows:
- Teams
- Live/final score
- Match phase
- Event feed
- Starting lineups
- Formation
- Substitutes
- Substitutions
- Goals
- Assists
- Cards
- Link back to tournament

---
# Public Player Page
**Route**
```text
/t/:slug/players/:playerId
```

Shows:
- Full name
- Known-as / nickname
- Photo
- Position(s)
- Shirt number
- Current team
- Tournament statistics
- Teams represented
- Match history
