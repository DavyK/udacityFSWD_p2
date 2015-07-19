__author__ = 'davidkavanagh'
import psycopg2


class TournamentDB():

    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self):
        self.db = psycopg2.connect("dbname=%s" % self.dbname)

    def cursor(self):
        self.cursor = self.db.cursor()
        return self.cursor()

    def query(self, q, d=None):
        self.cursor.execute(q, d)

    def commit(self):
        self.db.commit()

    def registerTournament(self, name):
        self.query("INSERT INTO tournament name VALUES %s", (name,))
        self.commit()

    def registerPlayer(self, name):
        self.query("INSERT INTO players name VALUES %s", (name,))
        self.commit()

    def countPlayers(self):
        self.query('SELECT count(*) as num FROM players')
        nPlayers = self.cursor.fecthone()[0]
        return nPlayers

    def countTournaments(self):
        self.query('SELECT count(*) as num FROM tournaments')
        nTournaments = self.cursor.fecthone()[0]
        return nTournaments

    def deletePlayers(self):
        self.query('DELETE FROM players')
        self.commit()

    def deleteMatches(self):
        self.query('DELETE FROM matches')
        self.commit()

    def deleteTournaments(self):
        self.query('DELETE FROM tournaments')
        self.commit()

