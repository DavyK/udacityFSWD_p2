#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import sys
import math
import random


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournaments")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute('DELETE FROM matches')
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute('DELETE FROM players')
    db.commit()
    db.close()


def deleteTournaments():
    """Remove all the tournament records from the database."""
    db = connect()
    c = db.cursor()
    c.execute('DELETE FROM tournaments')
    db.commit()
    db.close()

def deleteResults():
    """Remove all records from the player_tournament_results table"""
    db = connect()
    c = db.cursor()
    c.execute('DELETE FROM player_tournament_results')
    db.commit()
    db.close()


def countPlayers(tournament=None):
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    if tournament is not None:
        c.execute('SELECT count(player_id) from player_tournament_results WHERE tournament_id = %s', (tournament, ))
    else:
        c.execute('SELECT count(*) from players')
    result = c.fetchone()
    db.close()
    return result[0]


def countTournaments():
    """Returns the number of tournaments currently registered."""
    db = connect()
    c = db.cursor()
    c.execute('SELECT count(*) from tournaments')
    result = c.fetchone()
    db.close()
    return result[0]

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    db = connect()
    c = db.cursor()
    query = "INSERT INTO players (name) values (%s)"
    data = (name, )
    c.execute(query, data)
    db.commit()
    db.close

def registerTournament(name):
    """Adds a tournament to the tournament database.

    The database assigns a unique serial id number for the tournament.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the tournament's full name (need not be unique).

    Values:
        returns the id of the newly created tournament

    Note: added as support for multiple tournaments
    """

    db = connect()
    c = db.cursor()
    query = "INSERT INTO tournaments (name) values (%s) RETURNING id"
    data = (name, )
    c.execute(query, data)
    new_tournament_id = c.fetchone()[0]
    db.commit()
    db.close

    return new_tournament_id


def addPlayerToTournament(player, tournament):
    """Inserts record for player and tournament for keeping track of players scores across different tournaments.

    Args:
        player: id number of player to add.
        tournament: id number of tournament to which the player will be added.
    """

    db = connect()
    c = db.cursor()
    query = """
    INSERT INTO player_tournament_results
    VALUES (%s, %s)
    """
    data = (player, tournament)
    c.execute(query, data)
    db.commit()
    db.close()

def playerStandings(tournament=None):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
        id number of tournament. If None, standings are computed from all matches players have ever played.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db = connect()
    c = db.cursor()
    if tournament is not None:
        query = """
        SELECT id, name, wins, matches, score FROM tournament_standings
        WHERE tournament_id = %s
        """
        c.execute(query, (tournament,))

    else:
        query = """
        SELECT id, name, wins, matches, score FROM tournament_standings
        """
        c.execute(query)
    results = c.fetchall()

    db.close()

    if len(results) % 2 == 0:
        return results
    else:
        print "There are an odd number of players. Add another player please!"
        sys.exit(1)





def reportMatch(player1, player2, tournament, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      player1:  the id number of the player who won if draw=False
      player2:  the id number of the player who lost if draw=False
      draw: default = False, if true then both players drew.
    """

    db = connect()
    c = db.cursor()
    query = "INSERT INTO matches VALUES (%s, %s, %s, %s)"
    data = (tournament, player1, player2, draw)
    c.execute(query, data)
    db.commit()

    if not draw:
        query = """
        SELECT wins
        FROM
        player_tournament_results
        WHERE player_id = %s and tournament_id = %s
        """
        c.execute(query, (player2, tournament))
        player2_wins = c.fetchone()[0]

        query = """
        UPDATE player_tournament_results
        SET wins = wins + 1, score = score + %s
        WHERE player_id = %s and tournament_id = %s
        """
        c.execute(query, (player2_wins, player1, tournament,))

    else:
        query = """
        UPDATE player_tournament_results
        SET wins = wins + 0.5
        WHERE player_id IN (%s,%s) and tournament_id = %s
        """
        c.execute(query, (player1, player2, tournament,))

    query = """
    UPDATE player_tournament_results
    SET matches = matches + 1
    WHERE player_id IN (%s,%s) and tournament_id = %s
    """
    c.execute(query, (player1, player2, tournament))

    db.commit()
    db.close()


def swissPairings(tournament):
    """Returns a list of pairs of players for the next round of a match.

    Args:
        tournament - the id number of the tournament within which to ensure no duplicate matches
        and to calculate ties over.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db = connect()
    c = db.cursor()

    standings = playerStandings(tournament)
    pairings = []

    '''
    make a pool of players
    iterate over standings (which is sorted by wins, and then scores)
        if there are only two people left in the pool, find their ids, and names and add them to pairs
        else
        get all players this player has not previously played (eligible opponents)
        iterate over standings taking the first person that is in standings that is eligible.
        since standings is sorted this takes the person with closest score to the current player
        that they have not yet played, and that has not already been assigned to a match
    '''
    player_pool = [i[0] for i in standings]

    standings_dict = {p[0]: p for p in standings}

    for player in standings:
        if player[0] not in set(player_pool):
            # just in case
            continue

        elif len(player_pool) == 2:
            # make match with last 2 players as they are only choice
            p1 = standings_dict[player_pool[0]]
            p2 = standings_dict[player_pool[1]]
            pairings.append((p1[0], p1[1], p2[0], p2[1]))
            break
        else:
            query = """
                    SELECT id FROM players
                    WHERE id NOT IN
                    (
                        SELECT DISTINCT * FROM
                        (
                            SELECT player2_id FROM matches WHERE player1_id = %s AND tournament_id = %s
                            UNION
                            SELECT player1_id FROM matches WHERE player2_id = %s  AND tournament_id = %s
                        ) AS Q1
                    ) AND id != %s
                    """
            c.execute(query, (player[0], tournament, player[0], tournament, player[0]))

            # intersection off opponents not yet played against and opponents not yet assigned to a match
            eligible_opponents = set([r[0] for r in c.fetchall()]).intersection(set(player_pool))

            for o in standings:
                if o[0] in eligible_opponents:
                    pairings.append((player[0], player[1], o[0], o[1]))
                    del player_pool[player_pool.index(player[0])]
                    del player_pool[player_pool.index(o[0])]
                    break
    db.close()
    if len(pairings) == 0:
        print 'No more unique matches for this tournament exist!'
        sys.exit(1)

    return pairings

def runTournament():

    deleteMatches()
    deleteResults()
    deleteTournaments()
    deletePlayers()

    t = registerTournament('The Hunger Games')

    registerPlayer("Girl 1")
    registerPlayer("Boy 1")
    registerPlayer("Girl 2")
    registerPlayer("Boy 2")
    registerPlayer("Girl 3")
    registerPlayer("Boy 3")
    registerPlayer("Girl 4")
    registerPlayer("Boy 4")
    registerPlayer("Girl 5")
    registerPlayer("Boy 5")
    registerPlayer("Girl 6")
    registerPlayer("Boy 6")
    registerPlayer("Girl 7")
    registerPlayer("Boy 7")
    registerPlayer("Girl 8")
    registerPlayer("Boy 8")

    # The first time we call standings, leave tournament off
    standings = playerStandings()
    # since standings is sorted, but every one has a starting score of 0, shuffle for first round random pairings
    random.shuffle(standings)

    for i in standings:
        addPlayerToTournament(i[0], t)

    nPlayers = countPlayers(tournament=t)

    #print "There are {0} players competing in the tournament".format(nPlayers)

    round = 0
    while round < math.log(nPlayers, 2):
        pairs = swissPairings(t)
        for p in pairs:

            # randomly choose winner
            outcome = [0, 2]
            random.shuffle(outcome)
            winner = p[outcome[0]]
            looser = p[outcome[1]]

            # Randomly draw 1% of the time
            draw = False
            if random.randint(1, 100) == 1:
                draw = True
            reportMatch(winner, looser, draw=draw, tournament=t)
        round += 1

    print "The Winner is:", playerStandings(tournament=t)[0][1]

    deleteMatches()
    deleteResults()
    deleteTournaments()
    deletePlayers()

if __name__ == '__main__':
    runTournament()






