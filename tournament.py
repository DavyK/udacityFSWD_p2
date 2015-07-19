#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import sys
import math
import random


def connect(dbname="tournaments"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=%s" % dbname)


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


def deleteEntrants():
    """Remove all the tournament records from the database."""
    db = connect()
    c = db.cursor()
    c.execute('DELETE FROM players_in_tournaments')
    db.commit()
    db.close()


def countPlayers(tournament=None):
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
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
    query = "INSERT INTO players (name) values (%s) RETURNING id"
    data = (name, )
    c.execute(query, data)
    new_player_id = c.fetchone()[0]
    db.commit()
    db.close()
    return new_player_id


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
    db.close()

    return new_tournament_id


def addPlayerToTournament(player, tournament):

    db = connect()
    c = db.cursor()
    query = "INSERT INTO players_in_tournaments (player_id, tournament_id) values (%s, %s)"
    data = (player, tournament)
    c.execute(query, data)
    db.commit()
    db.close()


def playerStandings(tournament):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
        id number of tournament.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db = connect()
    c = db.cursor()
    query = """
        SELECT id, name, num_wins, num_matches FROM standings WHERE tournament_id = %s
        """
    c.execute(query, (tournament, ))
    results = c.fetchall()
    db.close()

    if len(results) % 2 != 0:
        print """
            Warning: There is an odd number of players. T
            his is not supported, and may yield strange results.
            Add another player please!
            """
    return results


def reportMatch(winner, looser, tournament, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      player1:  the id number of the player who won
      player2:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    query = """
    INSERT INTO matches (tournament_id, winner_id, looser_id, draw) VALUES (%s, %s, %s, %s)
    """
    data = (tournament, winner, looser, draw)
    c.execute(query, data)
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
            # if this player has already been assigned to a match, skip over them.
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
                            SELECT looser_id FROM matches WHERE winner_id = %s AND tournament_id = %s
                            UNION
                            SELECT winner_id FROM matches WHERE looser_id = %s  AND tournament_id = %s
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






