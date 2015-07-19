#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    # must delete before players, has reference to player id
    deleteEntrants()
    deletePlayers()
    print "2. Player records can be deleted."


def testDeleteTournament():
    # must delete before players, has reference to tournament id
    deleteEntrants()
    deleteTournaments()
    print "1a. Tournaments can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterTournament():
    deleteTournaments()
    registerTournament("Agni Kai")
    c = countTournaments()
    if c != 1:
        raise ValueError(
            "After one Tournament registers, countTournaments() should be 1.")
    print "4a. After registering a tournament, countTournaments() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testRegisterCountDeleteTournaments():
    deleteMatches()
    deleteTournaments()
    registerTournament("Agni Kai")
    registerTournament("Murder Ball")
    registerTournament("Death Frisbee")
    registerTournament("Ultimate Glass Eating")
    c = countTournaments()
    if c != 4:
        raise ValueError(
            "After registering four tournaments, countTournaments should be 4.")
    deleteTournaments()
    c = countTournaments()
    if c != 0:
        raise ValueError("After deleting, countTournaments should return zero.")
    print "5a. Tournaments can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    p1 = registerPlayer("Melpomene Murray")
    p2 = registerPlayer("Randy Schwartz")
    t = registerTournament('BAKE-OFF!!!')
    addPlayerToTournament(p1, t)
    addPlayerToTournament(p2, t)
    standings = playerStandings(t)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deleteEntrants()
    deleteTournaments()
    deletePlayers()

    players = (
        registerPlayer("Bruno Walton"),
        registerPlayer("Boots O'Neal"),
        registerPlayer("Cathy Burton"),
        registerPlayer("Diane Grant"),
        registerPlayer("Derek McFakeperson"),
        registerPlayer("Cody Neverexisted")
    )

    tournament = registerTournament("Grand Melee")

    for p in players:
        addPlayerToTournament(p, tournament)

    standings = playerStandings(tournament)

    [id1, id2, id3, id4, id5, id6] = [row[0] for row in standings]

    reportMatch(id1, id2, tournament=tournament)
    reportMatch(id3, id4, tournament=tournament)
    reportMatch(id5, id6, draw=True, tournament=tournament)

    standings = playerStandings(tournament)

    for (i, n, w, m) in standings:
        if m != 1:
            print standings
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            print standings
            raise ValueError("Each match loser should have zero wins recorded.")
        elif i in (id5, id6) and w != 1:
            raise ValueError("For players who drew, should have 1 wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deleteEntrants()
    deleteTournaments()
    deletePlayers()

    players = (
        registerPlayer("Twilight Sparkle"),
        registerPlayer("Fluttershy"),
        registerPlayer("Applejack"),
        registerPlayer("Pinkie Pie")
    )

    tournament = registerTournament("SPACE TAG")

    for p in players:
        addPlayerToTournament(p, tournament)

    standings = playerStandings(tournament)

    [id1, id2, id3, id4] = [row[0] for row in standings]

    reportMatch(id1, id2, tournament)
    reportMatch(id3, id4, tournament)

    pairings = swissPairings(tournament)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def runTournament():

    deleteMatches()
    deleteEntrants()
    deleteTournaments()
    deletePlayers()

    t = registerTournament('The Hunger Games')

    player_names = [
        "Girl 1",
        "Boy 1",
        "Girl 2",
        "Boy 2",
        "Girl 3",
        "Boy 3",
        "Girl 4",
        "Boy 4",
        "Girl 5",
        "Boy 5",
        "Girl 6",
        "Boy 6",
        "Girl 7",
        "Boy 7",
        "Girl 8",
        "Boy 8",
    ]

    # since standings is sorted, but every one has a starting score of 0, shuffle for first round random pairings
    random.shuffle(player_names)
    for n in player_names:
        p_id = registerPlayer(n)
        addPlayerToTournament(player=p_id, tournament=t)

    n_players = countPlayers()
    print "There are {0} players".format(n_players)

    tournament_round = 0
    while tournament_round < math.log(n_players, 2):
        pairs = swissPairings(t)
        for p in pairs:
            # randomly choose winner
            outcome = [0, 2]
            random.shuffle(outcome)
            winner = p[outcome[0]]
            looser = p[outcome[1]]

            # randomly draw 15% of the time
            draw = False
            if random.randint(1, 100) < 15:
                draw = True
            reportMatch(winner, looser,draw=draw, tournament=t)
        tournament_round += 1
    print "After {0} rounds....".format(tournament_round)

    final = playerStandings(tournament=t)
    winner = final[0]
    print "The Winner is {0} with {1} points".format(winner[1], winner[2])

    deleteMatches()
    deleteEntrants()
    deleteTournaments()
    deletePlayers()

if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()

    testDeleteTournament()
    testRegisterTournament()
    testRegisterCountDeleteTournaments()

    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success! All tests pass!"
    runTournament()


