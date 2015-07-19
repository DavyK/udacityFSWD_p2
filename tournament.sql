-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournaments;

CREATE database tournaments;

\c tournaments


CREATE TABLE players (
	id serial PRIMARY KEY,
	name text
);

CREATE TABLE tournaments (
	id	serial PRIMARY KEY,
	name	text
);

--for keeping track of which players are registered to which tournament
CREATE TABLE players_in_tournaments (
    id serial PRIMARY KEY,
    player_id serial REFERENCES players (id),
    tournament_id serial REFERENCES tournaments (id)
);
	
-- this table will hold all matches played in all tournaments. Each row will be uniquely identified by the combination of both players
-- and the tournament in which their match took place
-- assumption is that player 1 is the winner, unless draw is True, in which case, both players drew.
CREATE TABLE matches (
	id serial PRIMARY KEY,
	tournament_id serial REFERENCES tournaments (id),
	winner_id serial REFERENCES players (id),
	looser_id serial REFERENCES players (id),
	draw boolean
);

-- counts draws as a win for both players
CREATE VIEW player_win_count AS (
    SELECT players.id, players.name, COUNT(winner_id) as num_wins, players_in_tournaments.tournament_id
    FROM players LEFT JOIN matches ON players.id = matches.winner_id OR (players.id = matches.looser_id and draw = 't')
    LEFT JOIN players_in_tournaments ON players.id = players_in_tournaments.player_id
    GROUP BY players.id, players_in_tournaments.tournament_id
    ORDER BY num_wins DESC
);

CREATE VIEW player_match_count AS (
    SELECT players.id, players.name, COUNT(matches.id) as num_matches, players_in_tournaments.tournament_id
    FROM players LEFT JOIN matches ON players.id = matches.winner_id OR players.id = matches.looser_id
    LEFT JOIN players_in_tournaments ON players.id = players_in_tournaments.player_id
    GROUP BY players.id, players_in_tournaments.tournament_id
    ORDER BY num_matches DESC
);

-- combines player_match_counts and player_match_wins
CREATE VIEW player_standings AS (
    SELECT player_match_count.id, player_match_count.name, num_wins, num_matches, player_match_count.tournament_id
    FROM player_win_count, player_match_count
    WHERE player_win_count.id = player_match_count.id
    AND player_win_count.tournament_id = player_match_count.tournament_id
);

-- Looks messy, probably didn't need the outer most subquery but couldn't make it work otherwise.
-- finds opponents for everyone, joins with player standings on the opponents and sums the
-- wins of the opponents.
CREATE VIEW opponent_match_wins AS (
    SELECT p1 player_id, sum(num_wins) as omw
    FROM (
            SELECT p1, p2, num_wins
            FROM (
                    (
                        SELECT matches.id, matches.winner_id AS p1, matches.looser_id AS p2
                        FROM matches
                    )
                    UNION
                    (
                        SELECT matches.id, matches.looser_id AS p1, matches.winner_id AS p2
                        FROM matches
                    )
                ) AS q1, player_standings
            WHERE q1.p2 = player_standings.id
            ORDER BY p1
        )
    AS q2 GROUP BY p1
);

CREATE VIEW standings AS (
    SELECT * FROM player_standings LEFT JOIN opponent_match_wins ON id = player_id ORDER BY num_wins DESC, omw DESC
);



