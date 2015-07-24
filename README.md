# udacityFSWD_p2
udacity full stack web dev project 2

Tournament.py is intended to allow a user to interact with a Postgres database designed to
keep track of a swiss style tournament (https://en.wikipedia.org/wiki/Swiss-system_tournament).
the database can accept multiple tournaments, and tracks player standings within tournament only.
The standings are computed by the number of wins and the ties are broken by number of OMWs (Opponent Match Wins).
Currently an odd number of players is not supported, and rematches between the same opponent is allowed,
but only if there was no better pairing (based on wins and OMWs.


Requirments:
Virtual Box 4.3.28
Vagrant
Python 2.7+

This code is developed inside a vagrant virtual box VM.

run:
git clone http://github.com/udacity/fullstack-nanodegree-vm fullstack
cd fullstack/vagrant
vagrant up
vagrant ssh 

To obtain the same starting dev environment. 
By default the unmodified starting code of this project will live in the /vagrant/tournament directory of your VM.


Use the following commands to set up the db:
```
> pqsl

> \i tournament.sql

> \q
```
tournament.py
    tournament.py contains functions for interacting with the database - deleting and registering
    players, and tournaments, and players to tournaments.
    playerStandings() a function that takes as an argument the id number of the tournament to get the standings for.
    It returns a list of all players entered IN THAT TOURNAMENT sorted in decreasing order by their current scores,
    with ties broken by the sum of the number of wins
    of all previous opponents (OMW).

    swissPairings() returns all players entered in the requested tournament, paired by scores, and if possible, also by having
    never played each other before. I.E winners will be paired with winners, and losers with losers. Note that before the first
    round is played as all players will have a score of 0. This is why random.shuffle is used so that pairs will not be simply the
    order in which they were inserted into the DB tables.

    reportMatch() takes the winner and loser of match in that order, and optionally a draw argument that signifies that there was a draw.
    This function will update the matches table accordingly.

tournament_test.py
    This module contains some basic unit tests and a function runTournament() that shows how to:
        1) clear the database tables
        2) register tournament and players
        3) enter players into tournments
        4) pair players and randomly determine winner and/or a draw
        5) continue for the appropriate number of rounds based on the number of players ( log2(n) )

The run tournament_test.py to show unit tests, and one example of a tournament
```
> python tournament_test.py
    1. Old matches can be deleted.
    2. Player records can be deleted.
    3. After deleting, countPlayers() returns zero.
    4. After registering a player, countPlayers() returns 1.
    5. Players can be registered and deleted.
    1a. Tournaments can be deleted.
    4a. After registering a tournament, countTournaments() returns 1.
    5a. Tournaments can be registered and deleted.
    6. Newly registered players appear in the standings with no matches.
    7. After a match, players have updated standings.
    8. After one match, players with one win are paired.
    Success! All tests pass!
    There are 16 players
    After 4 rounds....
    The Winner is Boy 2 with 4 points
```






