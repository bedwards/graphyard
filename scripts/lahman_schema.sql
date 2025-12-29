-- Lahman Baseball Database Schema for PostgreSQL
-- Loaded into 'lahman' schema within graphyard database
-- Note: Foreign keys omitted for flexible loading from CSVs

-- Drop and recreate schema
DROP SCHEMA IF EXISTS lahman CASCADE;
CREATE SCHEMA lahman;

-- Set search path for this session
SET search_path TO lahman;

-- ============================================
-- CORE DIMENSION TABLES
-- ============================================

-- People (Players, Managers, etc.)
CREATE TABLE people (
    player_id VARCHAR(10) PRIMARY KEY,
    birth_year SMALLINT,
    birth_month SMALLINT,
    birth_day SMALLINT,
    birth_country VARCHAR(100),
    birth_state VARCHAR(100),
    birth_city VARCHAR(100),
    death_year SMALLINT,
    death_month SMALLINT,
    death_day SMALLINT,
    death_country VARCHAR(100),
    death_state VARCHAR(100),
    death_city VARCHAR(100),
    name_first VARCHAR(100),
    name_last VARCHAR(100),
    name_given VARCHAR(255),
    weight SMALLINT,
    height SMALLINT,
    bats VARCHAR(1),
    throws VARCHAR(1),
    debut VARCHAR(20),
    final_game VARCHAR(20),
    retro_id VARCHAR(20),
    bbref_id VARCHAR(20)
);

-- Teams
CREATE TABLE teams (
    year_id SMALLINT NOT NULL,
    lg_id VARCHAR(2),
    team_id VARCHAR(3) NOT NULL,
    franch_id VARCHAR(3),
    div_id VARCHAR(1),
    rank SMALLINT,
    games SMALLINT,
    games_home SMALLINT,
    wins SMALLINT,
    losses SMALLINT,
    div_win VARCHAR(1),
    wc_win VARCHAR(1),
    lg_win VARCHAR(1),
    ws_win VARCHAR(1),
    runs SMALLINT,
    at_bats SMALLINT,
    hits SMALLINT,
    doubles SMALLINT,
    triples SMALLINT,
    home_runs SMALLINT,
    walks SMALLINT,
    strikeouts_batting SMALLINT,
    stolen_bases SMALLINT,
    caught_stealing SMALLINT,
    hit_by_pitch SMALLINT,
    sacrifice_flies SMALLINT,
    runs_allowed SMALLINT,
    earned_runs SMALLINT,
    era DECIMAL(5,2),
    complete_games SMALLINT,
    shutouts SMALLINT,
    saves SMALLINT,
    outs_pitched INT,
    hits_allowed SMALLINT,
    home_runs_allowed SMALLINT,
    walks_allowed SMALLINT,
    strikeouts_pitching SMALLINT,
    errors SMALLINT,
    double_plays SMALLINT,
    fielding_pct DECIMAL(5,4),
    name VARCHAR(100),
    park VARCHAR(100),
    attendance INT,
    bpf SMALLINT,
    ppf SMALLINT,
    team_id_br VARCHAR(3),
    team_id_lahman45 VARCHAR(3),
    team_id_retro VARCHAR(3),
    PRIMARY KEY (year_id, team_id)
);

-- Franchises
CREATE TABLE teams_franchises (
    franch_id VARCHAR(3) PRIMARY KEY,
    franch_name VARCHAR(100),
    active VARCHAR(1),
    na_assoc VARCHAR(3)
);

-- Parks
CREATE TABLE parks (
    park_id VARCHAR(10) PRIMARY KEY,
    park_name VARCHAR(100),
    park_alias VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50)
);

-- Schools
CREATE TABLE schools (
    school_id VARCHAR(20) PRIMARY KEY,
    school_name VARCHAR(255),
    school_city VARCHAR(100),
    school_state VARCHAR(50),
    school_country VARCHAR(50)
);

-- ============================================
-- PERFORMANCE FACT TABLES
-- ============================================

-- Batting (Regular Season)
CREATE TABLE batting (
    player_id VARCHAR(10) NOT NULL,
    year_id SMALLINT NOT NULL,
    stint SMALLINT NOT NULL,
    team_id VARCHAR(3),
    lg_id VARCHAR(2),
    games SMALLINT,
    at_bats SMALLINT,
    runs SMALLINT,
    hits SMALLINT,
    doubles SMALLINT,
    triples SMALLINT,
    home_runs SMALLINT,
    rbi SMALLINT,
    stolen_bases SMALLINT,
    caught_stealing SMALLINT,
    walks SMALLINT,
    strikeouts SMALLINT,
    intentional_walks SMALLINT,
    hit_by_pitch SMALLINT,
    sacrifice_hits SMALLINT,
    sacrifice_flies SMALLINT,
    gidp SMALLINT,
    PRIMARY KEY (player_id, year_id, stint)
);

-- Pitching (Regular Season)
CREATE TABLE pitching (
    player_id VARCHAR(10) NOT NULL,
    year_id SMALLINT NOT NULL,
    stint SMALLINT NOT NULL,
    team_id VARCHAR(3),
    lg_id VARCHAR(2),
    wins SMALLINT,
    losses SMALLINT,
    games SMALLINT,
    games_started SMALLINT,
    complete_games SMALLINT,
    shutouts SMALLINT,
    saves SMALLINT,
    outs_pitched INT,
    hits SMALLINT,
    earned_runs SMALLINT,
    home_runs SMALLINT,
    walks SMALLINT,
    strikeouts SMALLINT,
    opponent_batting_avg DECIMAL(5,4),
    era DECIMAL(5,2),
    intentional_walks SMALLINT,
    wild_pitches SMALLINT,
    hit_batters SMALLINT,
    balks SMALLINT,
    batters_faced INT,
    games_finished SMALLINT,
    runs SMALLINT,
    sacrifice_hits SMALLINT,
    sacrifice_flies SMALLINT,
    gidp SMALLINT,
    PRIMARY KEY (player_id, year_id, stint)
);

-- Fielding (Regular Season)
CREATE TABLE fielding (
    player_id VARCHAR(10) NOT NULL,
    year_id SMALLINT NOT NULL,
    stint SMALLINT NOT NULL,
    team_id VARCHAR(3),
    lg_id VARCHAR(2),
    pos VARCHAR(2) NOT NULL,
    games SMALLINT,
    games_started SMALLINT,
    innings_outs INT,
    putouts SMALLINT,
    assists SMALLINT,
    errors SMALLINT,
    double_plays SMALLINT,
    passed_balls SMALLINT,
    wild_pitches SMALLINT,
    stolen_bases_against SMALLINT,
    caught_stealing_against SMALLINT,
    zone_rating DECIMAL(5,4),
    PRIMARY KEY (player_id, year_id, stint, pos)
);

-- ============================================
-- POSTSEASON TABLES
-- ============================================

-- Batting Post
CREATE TABLE batting_post (
    year_id SMALLINT NOT NULL,
    round VARCHAR(10) NOT NULL,
    player_id VARCHAR(10) NOT NULL,
    team_id VARCHAR(3),
    lg_id VARCHAR(2),
    games SMALLINT,
    at_bats SMALLINT,
    runs SMALLINT,
    hits SMALLINT,
    doubles SMALLINT,
    triples SMALLINT,
    home_runs SMALLINT,
    rbi SMALLINT,
    stolen_bases SMALLINT,
    caught_stealing SMALLINT,
    walks SMALLINT,
    strikeouts SMALLINT,
    intentional_walks SMALLINT,
    hit_by_pitch SMALLINT,
    sacrifice_hits SMALLINT,
    sacrifice_flies SMALLINT,
    gidp SMALLINT,
    PRIMARY KEY (year_id, round, player_id)
);

-- Pitching Post
CREATE TABLE pitching_post (
    player_id VARCHAR(10) NOT NULL,
    year_id SMALLINT NOT NULL,
    round VARCHAR(10) NOT NULL,
    team_id VARCHAR(3),
    lg_id VARCHAR(2),
    wins SMALLINT,
    losses SMALLINT,
    games SMALLINT,
    games_started SMALLINT,
    complete_games SMALLINT,
    shutouts SMALLINT,
    saves SMALLINT,
    outs_pitched INT,
    hits SMALLINT,
    earned_runs SMALLINT,
    home_runs SMALLINT,
    walks SMALLINT,
    strikeouts SMALLINT,
    opponent_batting_avg DECIMAL(5,4),
    era DECIMAL(5,2),
    intentional_walks SMALLINT,
    wild_pitches SMALLINT,
    hit_batters SMALLINT,
    balks SMALLINT,
    batters_faced INT,
    games_finished SMALLINT,
    runs SMALLINT,
    sacrifice_hits SMALLINT,
    sacrifice_flies SMALLINT,
    gidp SMALLINT,
    PRIMARY KEY (player_id, year_id, round)
);

-- Series Post
CREATE TABLE series_post (
    year_id SMALLINT NOT NULL,
    round VARCHAR(10) NOT NULL,
    team_id_winner VARCHAR(3),
    lg_id_winner VARCHAR(2),
    team_id_loser VARCHAR(3),
    lg_id_loser VARCHAR(2),
    wins SMALLINT,
    losses SMALLINT,
    ties SMALLINT,
    PRIMARY KEY (year_id, round)
);

-- ============================================
-- AWARDS AND RECOGNITION
-- ============================================

-- Awards Players
CREATE TABLE awards_players (
    player_id VARCHAR(10) NOT NULL,
    award_id VARCHAR(100) NOT NULL,
    year_id SMALLINT NOT NULL,
    lg_id VARCHAR(2) NOT NULL DEFAULT '',
    tie VARCHAR(1),
    notes VARCHAR(255),
    PRIMARY KEY (player_id, award_id, year_id, lg_id)
);

-- Hall of Fame
CREATE TABLE hall_of_fame (
    player_id VARCHAR(10) NOT NULL,
    year_id SMALLINT,
    voted_by VARCHAR(50) NOT NULL DEFAULT '',
    ballots SMALLINT,
    needed SMALLINT,
    votes SMALLINT,
    inducted VARCHAR(1),
    category VARCHAR(50),
    needed_note VARCHAR(100),
    PRIMARY KEY (player_id, year_id, voted_by)
);

-- All Star Full
CREATE TABLE allstar_full (
    player_id VARCHAR(10) NOT NULL,
    year_id SMALLINT NOT NULL,
    game_num SMALLINT NOT NULL DEFAULT 0,
    game_id VARCHAR(20),
    team_id VARCHAR(3),
    lg_id VARCHAR(2),
    gp SMALLINT,
    starting_pos SMALLINT,
    PRIMARY KEY (player_id, year_id, game_num)
);

-- ============================================
-- OTHER TABLES
-- ============================================

-- Salaries
CREATE TABLE salaries (
    year_id SMALLINT NOT NULL,
    team_id VARCHAR(3) NOT NULL,
    lg_id VARCHAR(2),
    player_id VARCHAR(10) NOT NULL,
    salary BIGINT,
    PRIMARY KEY (year_id, team_id, player_id)
);

-- Managers
CREATE TABLE managers (
    player_id VARCHAR(10),
    year_id SMALLINT NOT NULL,
    team_id VARCHAR(3) NOT NULL,
    lg_id VARCHAR(2),
    inseason SMALLINT NOT NULL DEFAULT 1,
    games SMALLINT,
    wins SMALLINT,
    losses SMALLINT,
    rank SMALLINT,
    plyr_mgr VARCHAR(1),
    PRIMARY KEY (year_id, team_id, inseason)
);

-- Appearances
CREATE TABLE appearances (
    year_id SMALLINT NOT NULL,
    team_id VARCHAR(3) NOT NULL,
    lg_id VARCHAR(2),
    player_id VARCHAR(10) NOT NULL,
    games_all SMALLINT,
    games_start SMALLINT,
    games_batting SMALLINT,
    games_defense SMALLINT,
    games_p SMALLINT,
    games_c SMALLINT,
    games_1b SMALLINT,
    games_2b SMALLINT,
    games_3b SMALLINT,
    games_ss SMALLINT,
    games_lf SMALLINT,
    games_cf SMALLINT,
    games_rf SMALLINT,
    games_of SMALLINT,
    games_dh SMALLINT,
    games_ph SMALLINT,
    games_pr SMALLINT,
    PRIMARY KEY (year_id, team_id, player_id)
);

-- College Playing
CREATE TABLE college_playing (
    player_id VARCHAR(10) NOT NULL,
    school_id VARCHAR(20),
    year_id SMALLINT NOT NULL,
    PRIMARY KEY (player_id, school_id, year_id)
);

-- Home Games
CREATE TABLE home_games (
    year_id SMALLINT NOT NULL,
    lg_id VARCHAR(2) NOT NULL DEFAULT '',
    team_id VARCHAR(3) NOT NULL,
    park_id VARCHAR(10),
    first_game VARCHAR(20),
    last_game VARCHAR(20),
    games SMALLINT,
    openings SMALLINT,
    attendance INT,
    PRIMARY KEY (year_id, lg_id, team_id, park_id)
);

-- ============================================
-- INDEXES FOR COMMON QUERIES
-- ============================================

CREATE INDEX idx_batting_player ON batting(player_id);
CREATE INDEX idx_batting_year ON batting(year_id);
CREATE INDEX idx_batting_team ON batting(team_id);

CREATE INDEX idx_pitching_player ON pitching(player_id);
CREATE INDEX idx_pitching_year ON pitching(year_id);
CREATE INDEX idx_pitching_team ON pitching(team_id);

CREATE INDEX idx_fielding_player ON fielding(player_id);
CREATE INDEX idx_fielding_year ON fielding(year_id);

CREATE INDEX idx_teams_year ON teams(year_id);
CREATE INDEX idx_teams_franch ON teams(franch_id);

CREATE INDEX idx_salaries_player ON salaries(player_id);
CREATE INDEX idx_salaries_year ON salaries(year_id);

CREATE INDEX idx_hof_inducted ON hall_of_fame(inducted);
CREATE INDEX idx_people_name ON people(name_last, name_first);
