-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

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
	
-- this table will hold all matches played in all tournaments. Each row will be uniquely identified by the combination of both players
-- and the tournament in which their match took place
-- assumption is that player 1 is the winner, unless draw is True, in which case, both players drew.
CREATE TABLE matches (
	tournament_id serial REFERENCES tournaments (id),
	player1_id serial REFERENCES players (id),
	player2_id serial REFERENCES players (id),
	draw boolean,
        primary key (tournament_id, player1_id, player2_id)
);

CREATE TABLE player_tournament_results (
    player_id serial REFERENCES players (id),
    tournament_id serial REFERENCES tournaments (id),
    wins float8 DEFAULT 0.0,
    matches integer DEFAULT 0.0,
	score float8 DEFAULT 0.0,
	primary key (player_id, tournament_id)
);

CREATE VIEW tournament_standings AS  (
    SELECT players.id, players.name, player_tournament_results.tournament_id,
    CASE WHEN player_tournament_results.wins IS NULL THEN 0 ELSE player_tournament_results.wins END,
    CASE WHEN player_tournament_results.matches IS NULL THEN 0 ELSE player_tournament_results.matches END,
    CASE WHEN player_tournament_results.score IS NULL THEN 0 ELSE player_tournament_results.score END
    FROM players LEFT JOIN player_tournament_results ON players.id = player_tournament_results.player_id
    ORDER BY player_tournament_results.wins DESC, player_tournament_results.score DESC
);
