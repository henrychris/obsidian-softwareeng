# Overview
A standalone tournament-management application for grassroots football organisers.

Hosts can configure a tournament, pay a one-time fee, manage the competition live, record match and player statistics, and share a real-time public tournament page.

**Price:** ₦2,000 per tournament.

Payment unlocks that specific tournament permanently.

QSet remains a separate pickup-game product and may direct tournament organisers into this application.

---
# Core Principles
1. **Simple tournaments should be easy to create.**
2. **Complex grassroots tournaments should still be supported within the V1 formats.**
3. **The host remains in control.** Avoid enforcing rules unless needed to preserve competition integrity.
4. **Competition history must never silently disappear.**
5. **Once competition begins, its competitive structure is frozen.**
6. **Everything shown publicly should update in real time.**
7. **Completed means final.** A completed tournament is permanently read-only.

---
# Tournament Lifecycle
Lifecycle:

```text
Draft → Active → In Progress → Completed
```

Visibility is separate from lifecycle:

```text
Published | Unpublished
```
## Draft
The tournament may be fully configured before payment.
### Authenticated users
Drafts persist and can be resumed later.
### Anonymous users
Anonymous users may configure the tournament through the Review step.

The draft is local only and may be lost if the user refreshes, clears browser data or leaves the flow.

An account is required before payment. After login/register, the current draft should be preserved, persisted to the account and returned to Review.
## Active
Payment activates that specific tournament permanently.
The tournament remains `Active` until its first match starts.
## In Progress
Starting the first match moves the tournament to `In Progress` and permanently applies the structural lock defined later in this specification.
## Completed
Completion is an explicit host action after all required competition matches are resolved and required awards have been selected.

`Completed` is permanently read-only and cannot be reopened.

---
# Tournament Setup
## Basic details
Required:
- Tournament name
- Description, maximum 500 characters
- Organiser, tied to the account
- Venue
- Start date
- Timezone

Optional:
- End date
- Logo
- Banner

V1 supports one venue per tournament, while the data model should remain extensible to multiple venues later.
## Team size
Host selects the number of players on the pitch per team, for example:
- 5-a-side
- 7-a-side
- 8-a-side
- 9-a-side
- 11-a-side
## Setup flow
The V1 creation flow is:
1. Basic Details
2. Competition Format
3. Players
4. Teams
5. Rosters / Team Assignment
6. Groups, where applicable
7. Fixtures
8. Review
9. Account, if anonymous
10. Payment
11. Tournament Dashboard

Each setup step explicitly saves and validates itself.

---
# Tournament Formats
V1 supports:
## Round Robin
Every team plays every other team.
Host chooses the number of fixture rounds.

Examples:
- 1 round → every opponent once
- 2 rounds → every opponent twice
## Knockout
Single-elimination bracket.

Byes are supported.

The host may reorder teams for seeding before competition begins.
## Group / League → Knockout
Supports:
- multiple groups
- fixture rounds within the group stage
- top N teams from each group qualifying
- best M remaining teams qualifying
- uneven group sizes

Teams are randomly distributed into groups as an unsaved initial allocation.

Before competition begins, the host may:
- move teams between groups
- reshuffle
- change the number of groups
- change qualification rules

Uneven groups are allowed, but the system should distribute teams as evenly as possible and warn the host.

---
# League Rules
Football scoring is fixed:
- Win: 3 points
- Draw: 1 point
- Loss: 0 points

Tiebreakers are applied in this order:
1. Points
2. Goal difference
3. Goals scored
4. Head-to-head
5. Fair play
6. Host decision

---
# Teams
Each team supports:
- Name, required
- Jersey colour, required
- Logo, optional
- Captain
- Roster

Team names must be unique within the tournament.

Minimum tournament team count is **2**.

Captain is informational only in V1 and may be changed while the tournament remains editable.

The captain must be an active player assigned to that team.

Every team must have a captain and meet its minimum roster requirement before the tournament can be published.
## Team withdrawal
After the first match begins:
- teams cannot be added
- teams cannot be deleted
- teams may only be withdrawn

Withdrawal:
- requires a reason
- requires a strong confirmation summarising its consequences
- cannot be reversed
- preserves all already completed results
- converts all remaining fixtures involving the withdrawn team into 3–0 walkovers for its opponents
- advances the opponent by 3–0 walkover when applicable in knockout competition
- is permanently audited

---
# Players & Rosters
Players exist only within a tournament.
## Player fields
Required:
- First name
- Last name
- Known-as / nickname
- One primary position

Optional / additional:
- Middle name
- Additional positions
- Photo

Players may exist without belonging to a team.

There is no cross-tournament player profile in V1.
## Team assignment
A player may be permanently assigned to only one team at a time.

While the tournament is editable, the host may:
- add new tournament players
- assign an unassigned player to a team
- move a player from Team A to Team B immediately
- move a player back to the unassigned pool
- mark a player inactive
- reactivate an inactive player
- edit player details

Historical appearances and statistics remain attributed to the team for which they were earned.

A player currently participating in a Live match cannot be reassigned until that match is no longer Live.

Roster/team-status changes require confirmation and are audited.
## Shirt numbers
Shirt number belongs to the **player-team assignment**, not the player globally.

Two players assigned to the same team cannot have the same active shirt number.

Historical match lineups preserve the shirt number used for that appearance.
## Match-level guests
Only **unassigned** tournament players may guest for a team at match level without permanently joining it.

A player permanently assigned to Team A cannot appear for Team B unless the host first changes their permanent team assignment.

The backend must validate player status and team allegiance before a match starts.

---
# Rosters & Publishing Requirements
Every team must meet a minimum roster size derived from the configured team size before roster setup can be completed and before publication.

There is no V1 maximum roster size unless introduced by a later product rule.
Unassigned tournament players are allowed and do not block publication.

A tournament may be published only when:
- payment is complete
- every team has a captain
- every team meets its minimum roster requirement
- every fixture has a date

Missing logos, banners and unassigned players do not block publication.

---
# Fixtures
The system automatically generates fixtures based on the competition structure.

During setup, generated fixtures are initially a preview until saved.
Host may assign and edit fixture dates/times.
Fixtures do not need to be played in generated order.
Multiple matches may be Live simultaneously.
## After competition begins
The host may:
- reorder upcoming fixtures
- change the date/time of unplayed fixtures
- reschedule postponed fixtures
- postpone fixtures
- cancel fixtures

The host may **not** add arbitrary fixtures that alter the locked competition structure.

If a fixture is cancelled, the host may create a **replacement fixture** representing the same competitive obligation. The replacement should be linked to the cancelled fixture in history/audit and must not increase the configured fixture rounds or otherwise change competition structure.
## Cancelled fixtures
A cancelled fixture:
- requires a reason
- remains visible to the host and audit history
- is hidden publicly
- does not count as Played
- does not affect standings
- does not advance a knockout bracket

---
# Match States

```text
Scheduled
Live
Postponed
Completed
Cancelled
```

Matches are never automatically completed by time.
The host controls match state.
A host may enter a completed result without first starting the match.
There is no single global “current match”; multiple fixtures may be Live at once.
## Match Resolution 
A completed match records how the result was resolved. 
```text 
Regulation
ExtraTime
Penalties
Walkover
```

`ResolutionType` is `null` until the match is completed.

Examples:
- Completed after regulation → `Regulation`
- Completed after extra time → `ExtraTime`
- Completed after a penalty shootout → `Penalties`
- Awarded as a walkover → `Walkover`
---
# Match Lineups
A lineup is required for a normal match.

A lineup is not required for a walkover.

Each lineup contains:
- Formation
- Exactly N starters, where N is the configured team size
- Zero or more substitutes

There is no minimum number of substitutes.

Formation presets depend on team size.

Example:
```text
5-a-side → 1-2-1, 2-1-1...
8-a-side → 2-3-2, 3-2-2...
11-a-side → 4-3-3, 4-2-3-1...
```

Eligible unassigned tournament players may appear as guests.
Lineups may be edited after kickoff for late arrivals. These changes are audited.
The backend must revalidate lineup eligibility, active status and team allegiance before match start.

---
# Goalkeepers & Clean Sheets
Any eligible player may be designated goalkeeper regardless of registered position.
An eligible unassigned guest may also be designated goalkeeper.

Goalkeeper designation is optional, with one symmetry rule:
- if one team designates a goalkeeper, the other team must also designate one

A designated goalkeeper receives a player clean sheet when:
- they participated for the team
- that team conceded zero goals

If neither side designates a goalkeeper, no clean sheets are awarded for a goalkeeper, although clean sheets are still assigned to all players on the team and the team as a unit.

---
# Substitutions
Record:
- player off
- player on
- event order

Rolling substitutions are supported.
A substituted player may return later.

V1 does not enforce substitution limits or tournament-specific substitution rules.

---
# Match Events
V1 events:
- Goal
- Assist
- Own goal
- Yellow card
- Red card
- Substitution
- Penalty shootout attempt

Events are ordered rather than timestamped by match minute.
## Goals
Every normal goal must have a scorer.

Assist is optional.
## Own goals
An own goal is attributed to:
- the conceding player
- the benefiting team

It contributes to an own-goal statistic, not the player's normal goal tally.
## Cards
Cards may be issued to starters or bench substitutes.
## Corrections
Events may be edited or deleted while the match/stage remains editable.
Corrections use an explicit Save action.
A completed match remains `Completed` while being corrected.

The UI warns that correcting a completed match may affect:
- score
- standings
- player statistics
- team statistics
- awards
- qualification
- bracket progression

Affected derived data is recalculated automatically.

---
# Knockout Match Flow
Knockout progression rule is configured by the host as one of:
- Straight to penalties
- Extra time → penalties
- Host decides per match

Scores are stored separately for:
- regulation
- extra time
- penalties

When a knockout match is completed: 
- regulation winner → `ResolutionType = Regulation`
- winner after extra time → `ResolutionType = ExtraTime`
- winner after shootout → `ResolutionType = Penalties`

Extra-time goals/events count normally and are tagged as Extra Time.
Penalty shootout attempts are tracked individually.
Shootout goals do **not** contribute to normal player goal statistics.
Final review displays the overall score, phase scores where relevant, events and winner.

---
# Postponed Matches
A Live match may be postponed.

Postponement preserves:
- current score
- lineups
- substitutions
- events
- cards
- current phase
- audit history

While `Postponed`, the fixture:
- does not count as Played
- does not affect standings
- does not advance a knockout bracket
- does not count toward tournament completion

The host may later choose:
## Continue Match
Resume the same fixture and preserved match state.
## Restart Match
Restart the same fixture ID from 0–0.
The abandoned attempt remains in audit/history, but its prior events cease contributing to official score/statistics.

A fresh lineup may be entered.
No duplicate fixture is created.

---
# Walkovers
A walkover is a completed-match resolution, not a separate match state. 

Awarding a walkover: 
- sets the match state to `Completed`
- sets `ResolutionType = Walkover`
- awards a fixed 3–0 result
- does not require a lineup 

If an ordinary completed match is corrected to a walkover while corrections are still permitted: 
- `ResolutionType` changes to `Walkover` 
- the 3–0 walkover becomes the official result 
- prior normal-match events stop contributing to official statistics 
- those events remain preserved in audit/history

---
# Stage Corrections & Locks
Completed matches may be corrected while their competition stage remains editable.
A stage remains editable **until the first match in the succeeding stage is completed**.

Examples:
- Group-stage results may be corrected after knockout fixtures have started, provided no knockout match has yet been completed.
- Once the first knockout match is completed, the group stage becomes permanently frozen.

For round-robin tournaments with no succeeding stage, corrections remain allowed until the tournament itself is completed.
If a correction changes standings but not qualification, standings recalculate normally.

If a correction changes qualification and the succeeding stage has no completed matches yet:
- qualifiers update automatically
- affected future knockout participants update automatically
- scheduled but unplayed knockout fixtures may therefore change participants

The UI must warn when a correction could affect qualification or bracket progression. Something like: "Correcting this result may change who qualifies from this group, which could change the teams in an already-scheduled knockout fixture. Continue?"

When a prior stage is locked, the UI should explain why, e.g.:
> Group-stage results are locked because a knockout match has already been completed.
---
# Statistics
Automatically track:
## Team
- Played
- Wins
- Draws
- Losses
- Goals for
- Goals against
- Goal difference
- Points
- Clean sheets
- Cards
## Player
- Goals
- Assists
- Own goals
- Yellow cards
- Red cards
- Clean sheets
- Appearances
- Teams represented

Tournament-level player aggregate statistics remain with the player even if they change teams.

---
# Awards
## Automatically calculated
- Top Scorer
- Top Assists
- Best Goalkeeper
- Most Yellow Cards
- Most Red Cards

Best Goalkeeper is determined by **goalkeeper clean sheets**.
If multiple goalkeepers have the highest clean-sheet total, they are joint winners.
Other statistical awards may also have joint winners.
## Host-selected
Before completing the tournament, the host must select:
- MVP / Player of the Tournament
- Best Defender
- Best Midfielder
- Best Forward

There is no built-in voting system in V1. Hosts may run voting outside the product if they wish.

---
# Public Tournament Experience
After payment, the tournament is `Unpublished` by default.

Host may:
- preview the public experience before publishing
- publish
- unpublish, including while matches are Live

An unpublished public route returns **404**.
Tournaments are unlisted; there is no discovery directory in V1.
The public slug is generated for the tournament and remains constant. Renaming the tournament does not change it.
## Public tournament page
Shows, as relevant:
- overview
- live matches
- fixtures and results
- groups
- standings
- knockout bracket
- teams
- players, including unassigned players where appropriate
- player/team statistics
- awards
- audit history

All live competition information updates in real time.
## Public player page
Shows:
- Full name
- Known-as name
- Photo
- Position(s)
- Current team
- Current team-specific shirt number, where assigned
- Statistics
- Match history
## Completed tournament presentation
After completion, the public experience prioritises:
1. Champion
2. Awards
3. Final standings / knockout bracket
4. Tournament statistics
5. Matches and results
6. Teams
7. Players
8. Audit history

A completed tournament remains accessible according to its final publishing state.

---
# Live Match Page
Every published match has a shareable public page.

When Live, it shows:
- score
- match phase
- event feed
- starting lineups
- substitutes
- substitutions
- cards
- goals/assists
- link back to tournament

Updates appear in real time without refresh.
The tournament homepage includes a **Live Now** section whenever one or more matches are active.

---
# Audit Log
Every meaningful mutation is recorded permanently.

Examples:
- tournament details changed
- fixture changed
- replacement fixture created
- team withdrawn
- player created/edited
- roster/team assignment changed
- player activated/inactivated
- shirt number changed
- lineup changed
- goal/card/event corrected
- result corrected
- match postponed/restarted
- fixture cancelled
- tournament published/unpublished
- awards selected
- tournament completed

Where meaningful, public audit entries show **before → after** values.

V1 displays the actor publicly as:

> Tournament Host

The backend stores the actual user responsible for the action.
Audit records are permanent and never deleted.

---
# Payment & Activation
Tournament fee:

**₦2,000 once per tournament.**

Before payment, the host may:
- configure tournament details
- add teams and players
- configure rosters
- configure groups/brackets
- generate and review fixtures
- preview the public page

Before payment, the host may not:
- operate live matches
- record played-match data
- publish the tournament

Account/login is required before payment.
Payment permanently activates that specific tournament.

Deleting the tournament:
- does not restore the entitlement
- does not grant a replacement tournament
- does not produce a refund

Payments are non-refundable. There is no tournament reset.

---
# Structural Lock
## Before first match starts
Competition structure remains editable.
Structural changes may regenerate affected groups, fixtures or brackets after confirmation.
## Once first match starts
The following become permanently locked:
- tournament format
- team size
- participating teams
- number of groups
- group membership
- qualification rules
- fixture rounds / competition structure

The host may not add arbitrary fixtures that change those rules.

Operational information remains editable until completion, subject to stage locks:
- tournament name/details
- venue
- logos/photos
- player information
- roster/team assignments
- player active status
- captain assignments
- fixture scheduling
- lineups
- substitutions
- results
- match events

Teams are withdrawn rather than deleted.
Players are made inactive rather than deleted.
Past competition history is preserved.

---
# Tournament Completion
The application detects when all required competition fixtures are resolved and prompts the host to review and complete the tournament.

Resolved fixtures include:
- Completed matches, regardless of resolution type
- Cancelled fixtures that no longer require a replacement
## Final review
Before completion, the host reviews:
- champion
- final standings and/or bracket
- group winners/qualifiers where applicable
- match completion summary
- automatic awards
- host-selected awards
- unresolved warnings

Required host-selected awards must be selected before completion:
- MVP / Player of the Tournament
- Best Defender
- Best Midfielder
- Best Forward

The host may return and make permitted corrections before completing.
## Confirmation
Completion requires an explicit confirmation warning that the action is irreversible.

Suggested meaning:

> Once completed, the tournament becomes permanently read-only. Results, matches, teams, players, rosters, awards and tournament settings can no longer be changed. This cannot be undone.
## After completion
Status changes:
```text
In Progress → Completed
```

Immediately after completion:
- matches and events are read-only
- lineups/substitutions are read-only
- standings/brackets are read-only
- teams are read-only
- players are read-only
- rosters and shirt numbers are read-only
- awards are read-only
- tournament settings/configuration are read-only
- audit history remains accessible

There is **no correction window** and no separate `Locked` status.
The tournament cannot be reopened.

---
# V1 Out of Scope
- Player tiers
- Captain drafting
- Captain accounts
- Co-admins / granular permissions
- MVP/public voting
- Player registration/payment collection
- Suspension-rule engine
- Referee accounts
- Notification system
- Tournament discovery feed
- Multiple venues
- Native mobile applications
- Tournament chat
- Cross-tournament player profiles
- Automated kickoff/end timers
- Enforcement of substitution rules
- Arbitrary/custom competition-format builder
