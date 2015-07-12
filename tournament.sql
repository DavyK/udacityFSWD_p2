-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

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
CREATE TABLE matches (
	tournament_id serial REFERENCES tournaments (id),
	player_id1 serial REFERENCES players (id),
	player_id2  serial REFERENCES players (id), 
	winner text,
        primary key (tournament_id, player_id1, player_id2)
);

-- We could allow scores in the player table but when supporting multiple tournaments, we might want to the score of a new tournament not
-- not to depend on the scores from previous ones. If score is stored in player the everytime there is a new tournament, the old scores might get lost. 
-- Our schema should not enforce this behaviour. It should be a decision for each tournament whether scores depend on old scores, or start fresh.
CREATE TABLE tournament_scores (
	player_id serial REFERENCES players (id),
	tournament_id serial REFERENCES tournaments (id),
	score float8,
	primary key (player_id, tournament_id)
);
