# Origin
In November 2024, Ibidapo and I (Henry) went to play ball at a pitch in Gbagada. At some point, the various teams started to argue about when would be their turn to play. This argument dragged on for 10 minutes, before they finally settled and the play resumed. Of course, they would later have a similar argument.

This is a problem that often occurs when playing football in Nigeria. People are unable to keep track of the order of the various teams, as there are many factors to consider: how many wins does a team have? How many teams are there? Assuming they drew last time they played, who is to come in first?

That evening, we built the very first version of QSet.
# The Core Idea
QSet is a match tracker and queue manager for casual football sessions — especially "winner-stays-on" games. It helps players:
- Track who's on the pitch
- Know who’s next
- Record match results
- Keep the game flowing without fights
# MVP Features
I will be discussing the features in the current version of QSet.
## Team Setup
Users can add as many teams as they would like, and change their names. The interface allows for quick team management before starting a game session.

Users can shuffle the order of teams, such that they are randomised in the queue. The order can be reset as well, returning teams to their original arrangement.

**Note for design:** The checkbox to assign teams currently exists but is unused and will be removed shortly. We intend to redesign and bring it back in the future.
![[qset-mvp-1.png]]
![[qset-mvp-2.png]]
## Game Flow
After the user taps/clicks 'Start Game', users are taken to the **Game View**.
![[qset-mvp-3.png]]
This is divided into sections:
### Navigation & Controls
After the user taps/clicks 'Start Game', they see the main game screen. The interface has multiple pages that can be accessed during gameplay. On desktop, users can click navigation buttons to move between pages. On mobile, they can swipe any part of the screen to navigate.

![[qset-mvp-4.png]]
The undo and redo buttons allow users to undo or redo the last actions they performed. Mistakes are common when using QSet during live games, so we allow users to easily fix these errors without disrupting the flow.
![[qset-mvp-5.png]]
### Current Match Display
The main section shows which teams are currently playing each other. A timer counts down how many minutes are left in the game, and this duration can be configured by users.
![[qset-mvp-6.png]]
Each team displays a flame icon that represents their streak—how many matches they've won in a row. This gives players immediate visual feedback about team performance.

The arrow button swaps the team in the match with the first team in the queue. This feature handles situations where a new team joins mid-game, and the people on ground decide to let them play before continuing with the normal queue system.

The pencil button allows users to edit team names directly during gameplay, accommodating changes without interrupting the match flow:
![[qset-mvp-7.png]]
#### Match Resolution
Three buttons handle match outcomes: "TEAM1 Wins", "Draw", and "TEAM2 Wins". Each button triggers a specific sequence of events.

When "TEAM1 Wins" is clicked, a loss is recorded for TEAM2, and they are pushed to the end of the queue. A win is recorded for TEAM1 and their streak increases by 1. The first team in the queue replaces TEAM2 in the match.

When "TEAM2 Wins" is clicked, a loss is recorded for TEAM1, and they are pushed to the end of the queue. A win is recorded for TEAM2 and their streak increases by 1. The first team in the queue replaces TEAM1 in the match.

When "Draw" is clicked, a draw is recorded for both teams and both are pushed to the end of the queue. The team that has won fewer games enters the queue first, but if they have the same number of wins, the team in the second slot enters the queue first.
### Timer Configuration
The timer can be configured and counts down how many minutes are left in the match. Users can set custom durations or select from preset options like 7 minutes or 10 minutes. The timer provides visual feedback about match progress and helps maintain consistent game lengths.
![[qset-mvp-8.png]]
![[qset-mvp-9.png]]
### Queue Management
The queue section shows how many teams are waiting in line and in what order they will play. Users can move teams up and down in the queue using arrow buttons, allowing for real-time adjustments based on field conditions.
![[qset-mvp-10.png]]
The pencil button enables name editing for teams in the queue, while the trash icon removes a team from the game entirely. These actions help accommodate the dynamic nature of pickup football games.
### Adding Teams
A text field and plus button allow users to add new teams to the queue during gameplay. The reset button restarts the entire game, deletes all current data, and returns users to the initial team setup screen.
![[qset-mvp-11.png]]
## Other Screens
### League Table
The standings screen displays a comprehensive league table showing wins, draws, losses, and points accumulated by each team during the current game session. This table can be shared with other players or downloaded for record-keeping purposes.
![[qset-mvp-12.png]]
![[qset-mvp-13.png]]
### Match History
The history screen shows a chronological record of all matches played in the current game session, including the result of each match. This provides a complete audit trail of the game's progression.
![[qset-mvp-14.png]]
# Supporting Features
## Guide Page
The guide explains how to use QSet, but it's currently outdated. According to PostHog data, this page is often unvisited, suggesting users either find the app intuitive or prefer learning through direct interaction.
![[qset-mvp-15.png]]
## Feedback Page
The feedback page exists to collect user input and suggestions. This helps us understand how QSet performs in real-world conditions and what improvements users need most. However, we have not received feedback via this route since the week we released QSet.
![[qset-mvp-16.png]]
# Technical Context
QSet is designed mobile-first, with touch interactions as the primary input method. The desktop version adapts these interactions to work with mouse clicks, but the core experience prioritises mobile usage since most players use phones during pickup games.
# Design Considerations
The interface must work well in outdoor conditions where lighting can be challenging and users might be wearing gloves or have wet hands. Actions should be clearly distinguishable to prevent accidental selections during fast-paced game management.

The queue visualisation is particularly important since it's the core feature that solves the original problem. Players need to instantly understand who's playing next and where their team stands in the order.

Error prevention is crucial during live games, but when mistakes do happen, the undo/redo system should make corrections quick and obvious. The balance between preventing accidents and maintaining speed is key to the user experience.

Actions should require minimal taps. We aim to reduce the number of buttons.