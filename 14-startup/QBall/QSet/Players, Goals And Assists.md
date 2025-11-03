# Description
From the start, users have asked us to support adding players to teams so that they can record stats. This supports one of  our goals for QSet \- virality. We can achieve that by adding features that encourage users to share. Sharing equals more eyes. More eyes means more organic usage. Until one day \- it blows up. Now, for the requirements.
## Setup
The current setup flow only accepts team names. We need to update it so that users can also add players to their teams. All teams have the same number of players. However, teams tend to reuse goalkeepers, so that must be considered.
## Game
With the addition of players, we can now record goals and assists. This means the current interface:  
![[Pasted image 20251003085907.png]]
Should instead record goals, instead of ‘TEAM 1 Wins’, ‘TEAM 2 Wins’ or ‘Draw’. We can add a button to end the match, then the system deciphers the result to determine if a team won or lost, or if the match ended as a draw.  

For every goal, if a team has players \- let’s assume users may not want to take the time to add players to teams \- we prompt them to select who scored and who assisted. 

But there’s another thing to consider \- teams tend to borrow players. We need to cover for this by allowing users to choose players from the player pool \- outside of the current team \- as the one who scored or assisted. 

We should also be able to record own goals.
## Statistics
As the game goes on, we must record the statistics for every player and display the data in an easy to view format. We must show goals, assists and own goal statistics. We should also be able to share these stats in a format optimised for social media. We should also add a session summary feature, showing the top team, top goal scorer and the player with the most assists.
## Table
The table will be updated as well to include goals for, goals against and goal difference.
# Prompt
i am working on a new QSet feature. some details here:

From the start, users have asked us to support adding players to teams so that they can record stats. This supports one of  our goals for QSet \- virality. We can achieve that by adding features that encourage users to share. Sharing equals more eyes. More eyes means more organic usage. Until one day \- it blows up. Now, for the requirements.
# Setup
The current setup flow only accepts team names. We need to update it so that users can also add players to their teams. All teams have the same number of players. However, teams tend to reuse goalkeepers, so that must be considered.
# Game
With the addition of players, we can now record goals and assists. This means the current interface:  
![[Pasted image 20251003085907.png]]
Should instead record goals, instead of ‘TEAM 1 Wins’, ‘TEAM 2 Wins’ or ‘Draw’. We can add a button to end the match, then the system deciphers the result to determine if a team won or lost, or if the match ended as a draw.  

For every goal, if a team has players \- let’s assume users may not want to take the time to add players to teams \- we prompt them to select who scored and who assisted. 

But there’s another thing to consider \- teams tend to borrow players. We need to cover for this by allowing users to choose players from the player pool \- outside of the current team \- as the one who scored or assisted. 

We should also be able to record own goals.
# Statistics
As the game goes on, we must record the statistics for every player and display the data in an easy to view format. We must show goals, assists and own goal statistics. We should also be able to share these stats in a format optimised for social media. We should also add a session summary feature, showing the top team, top goal scorer and the player with the most assists.
# Table
The table will be updated as well to include goals for, goals against and goal difference.

I will attach images showing the UI and describe how it ought to work:

first, as the user clicks the +/- button to add or remove teams , the new teams are stacked atop one another.

each team card has a name, and two buttons: Customize & trash icon (delete). We can use a pencil for customise on small screens.

If the user clicks customise, we move to the next screen for customising a team and adding players. this is new.

At the top, they can edit the team name. We will show an error if it matches other teams in the game.

There is a button to add players to the team. this adds input fields for player name, next to an X icon for removing said player. Below is a reset icon that rmeoves al players & resets the team name. Below that is a save button. Saving persists the changes and adds the players to the player pool.
This player pool is used for subsequent teams. We need to let users know when a player with a certain name is on another team.

Saving or pressing back returns to the main screen showing the team overview. If a team has players, we show the number of players as subscript below their name.

When they hit continue, we will check if all teams have the same number of players, if not, we show a warning before they continue. 

if they try to delete a team, we show a warning as well to try and prevent data loss.

#codebase 