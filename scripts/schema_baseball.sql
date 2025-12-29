-- Consolidated Baseball Schema
-- Unifies Lahman, Retrosheet, and Statcast data with proper foreign keys

CREATE SCHEMA IF NOT EXISTS baseball;

-- =============================================================================
-- MASTER TABLES: Single source of truth for players, teams, games
-- =============================================================================

-- Master Players table - links all ID systems
CREATE TABLE IF NOT EXISTS baseball.players (
    id SERIAL PRIMARY KEY,

    -- Lahman ID (primary key in most baseball databases)
    lahman_id VARCHAR(10) UNIQUE,            -- e.g., "ruthba01"

    -- Retrosheet ID
    retrosheet_id VARCHAR(10),               -- e.g., "ruthb101"

    -- MLB.com ID (used by Statcast)
    mlb_id INTEGER UNIQUE,                   -- e.g., 545361

    -- Baseball Reference ID
    bbref_id VARCHAR(10),

    -- Biographical info (from Lahman)
    name_first VARCHAR(100),
    name_last VARCHAR(100),
    name_given VARCHAR(200),
    birth_date DATE,
    death_date DATE,
    birth_country VARCHAR(100),
    birth_state VARCHAR(100),
    birth_city VARCHAR(100),
    bats CHAR(1),                            -- L, R, B
    throws CHAR(1),                          -- L, R
    height_inches SMALLINT,
    weight_lbs SMALLINT,
    debut_date DATE,
    final_game_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_players_lahman ON baseball.players(lahman_id);
CREATE INDEX idx_players_mlb ON baseball.players(mlb_id);
CREATE INDEX idx_players_name ON baseball.players(name_last, name_first);

-- Master Teams table
CREATE TABLE IF NOT EXISTS baseball.teams (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(3) NOT NULL,             -- LAA, NYY, etc.
    franchise_id VARCHAR(3),
    league VARCHAR(2),                       -- AL, NL
    division VARCHAR(1),                     -- E, C, W
    name VARCHAR(100),
    park VARCHAR(100),
    year_founded SMALLINT,
    year_defunct SMALLINT,
    UNIQUE(team_id, year_founded)
);

-- Master Games table - links game identifiers
CREATE TABLE IF NOT EXISTS baseball.games (
    id SERIAL PRIMARY KEY,
    game_pk BIGINT UNIQUE,                   -- MLB game ID (Statcast)
    retrosheet_game_id VARCHAR(20),          -- e.g., "LAN202403200"
    game_date DATE NOT NULL,
    home_team_id INTEGER REFERENCES baseball.teams(id),
    away_team_id INTEGER REFERENCES baseball.teams(id),
    home_score SMALLINT,
    away_score SMALLINT,
    venue VARCHAR(100),
    attendance INTEGER,
    game_type VARCHAR(1),                    -- R=regular, P=postseason
    day_night VARCHAR(1),                    -- D, N
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_games_date ON baseball.games(game_date);
CREATE INDEX idx_games_pk ON baseball.games(game_pk);

-- =============================================================================
-- STATCAST: Pitch-by-pitch tracking data (2015+)
-- =============================================================================

CREATE TABLE IF NOT EXISTS baseball.statcast_pitches (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES baseball.games(id),
    game_pk BIGINT,                          -- MLB game ID
    game_date DATE,
    at_bat_number SMALLINT,
    pitch_number SMALLINT,

    -- Players (FK to master table)
    pitcher_id INTEGER REFERENCES baseball.players(id),
    batter_id INTEGER REFERENCES baseball.players(id),
    pitcher_mlb_id INTEGER,                  -- Original Statcast ID
    batter_mlb_id INTEGER,

    -- Pitch characteristics
    pitch_type VARCHAR(5),                   -- FF, SL, CH, CU, etc.
    release_speed DECIMAL(5,2),              -- mph
    release_spin_rate INTEGER,               -- rpm
    release_pos_x DECIMAL(6,3),              -- ft from center
    release_pos_z DECIMAL(6,3),              -- ft from ground
    pfx_x DECIMAL(6,3),                      -- horizontal movement (in)
    pfx_z DECIMAL(6,3),                      -- vertical movement (in)
    plate_x DECIMAL(6,3),                    -- location at plate
    plate_z DECIMAL(6,3),
    zone SMALLINT,                           -- strike zone location

    -- Batted ball (if contact)
    launch_speed DECIMAL(5,2),               -- exit velocity (mph)
    launch_angle DECIMAL(6,2),               -- degrees
    hit_distance INTEGER,                    -- projected (ft)
    bb_type VARCHAR(20),                     -- ground_ball, fly_ball, etc.
    hc_x DECIMAL(7,2),                       -- hit coordinates
    hc_y DECIMAL(7,2),

    -- Expected stats
    estimated_ba DECIMAL(5,4),               -- xBA
    estimated_woba DECIMAL(5,4),             -- xwOBA

    -- Result
    events VARCHAR(50),                      -- single, strikeout, home_run, etc.
    description VARCHAR(100),                -- play description
    type CHAR(1),                            -- B=ball, S=strike, X=in play

    -- Count
    balls SMALLINT,
    strikes SMALLINT,
    outs_when_up SMALLINT,
    inning SMALLINT,
    inning_topbot VARCHAR(3),                -- Top, Bot

    -- Game context
    home_team VARCHAR(3),
    away_team VARCHAR(3),
    stand CHAR(1),                           -- L, R
    p_throws CHAR(1),                        -- L, R
    on_1b INTEGER,                           -- runner MLB ID
    on_2b INTEGER,
    on_3b INTEGER,
    home_score SMALLINT,
    away_score SMALLINT,

    -- Bat tracking (2024+)
    bat_speed DECIMAL(5,2),
    swing_length DECIMAL(5,2)
);

CREATE INDEX idx_statcast_date ON baseball.statcast_pitches(game_date);
CREATE INDEX idx_statcast_pitcher ON baseball.statcast_pitches(pitcher_id);
CREATE INDEX idx_statcast_batter ON baseball.statcast_pitches(batter_id);
CREATE INDEX idx_statcast_pitch_type ON baseball.statcast_pitches(pitch_type);
CREATE INDEX idx_statcast_events ON baseball.statcast_pitches(events);

-- =============================================================================
-- RETROSHEET: Game logs (1871+)
-- =============================================================================

CREATE TABLE IF NOT EXISTS baseball.retrosheet_gamelogs (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES baseball.games(id),
    retrosheet_game_id VARCHAR(20),
    game_date DATE NOT NULL,
    game_number SMALLINT,                    -- 0=single, 1=first, 2=second
    day_of_week VARCHAR(3),

    -- Teams
    visiting_team VARCHAR(3),
    visiting_league VARCHAR(2),
    visiting_game_number SMALLINT,
    home_team VARCHAR(3),
    home_league VARCHAR(2),
    home_game_number SMALLINT,

    -- Score
    visitor_score SMALLINT,
    home_score SMALLINT,
    length_outs SMALLINT,                    -- game length in outs
    day_night CHAR(1),

    -- Venue
    park_id VARCHAR(10),
    attendance INTEGER,
    duration_minutes SMALLINT,

    -- Line scores
    visitor_line_score VARCHAR(30),
    home_line_score VARCHAR(30),

    -- Offensive stats
    visitor_at_bats SMALLINT,
    visitor_hits SMALLINT,
    visitor_doubles SMALLINT,
    visitor_triples SMALLINT,
    visitor_home_runs SMALLINT,
    visitor_rbi SMALLINT,
    visitor_walks SMALLINT,
    visitor_strikeouts SMALLINT,
    visitor_stolen_bases SMALLINT,
    visitor_errors SMALLINT,

    home_at_bats SMALLINT,
    home_hits SMALLINT,
    home_doubles SMALLINT,
    home_triples SMALLINT,
    home_home_runs SMALLINT,
    home_rbi SMALLINT,
    home_walks SMALLINT,
    home_strikeouts SMALLINT,
    home_stolen_bases SMALLINT,
    home_errors SMALLINT,

    -- Umpires
    hp_umpire_id VARCHAR(10),
    hp_umpire_name VARCHAR(100),

    -- Managers
    visitor_manager_id VARCHAR(10),
    visitor_manager_name VARCHAR(100),
    home_manager_id VARCHAR(10),
    home_manager_name VARCHAR(100),

    -- Pitchers
    winning_pitcher_id VARCHAR(10),
    losing_pitcher_id VARCHAR(10),
    save_pitcher_id VARCHAR(10),

    -- Starting pitchers
    visitor_starting_pitcher_id VARCHAR(10),
    home_starting_pitcher_id VARCHAR(10),

    -- Completion info
    completion_info VARCHAR(100),
    forfeit_info VARCHAR(10),
    protest_info VARCHAR(10),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_retrosheet_date ON baseball.retrosheet_gamelogs(game_date);
CREATE INDEX idx_retrosheet_home ON baseball.retrosheet_gamelogs(home_team);
CREATE INDEX idx_retrosheet_visitor ON baseball.retrosheet_gamelogs(visiting_team);

-- =============================================================================
-- VIEWS: Unified access across data sources
-- =============================================================================

-- Player lookup with all IDs
CREATE OR REPLACE VIEW baseball.player_ids AS
SELECT
    p.id,
    p.lahman_id,
    p.retrosheet_id,
    p.mlb_id,
    p.name_first,
    p.name_last,
    p.name_first || ' ' || p.name_last AS full_name,
    p.debut_date,
    p.final_game_date
FROM baseball.players p;

COMMENT ON SCHEMA baseball IS 'Consolidated baseball data from Lahman, Retrosheet, and Statcast';
COMMENT ON TABLE baseball.players IS 'Master player table linking all ID systems';
COMMENT ON TABLE baseball.statcast_pitches IS 'Statcast pitch-by-pitch tracking data (2015+)';
COMMENT ON TABLE baseball.retrosheet_gamelogs IS 'Retrosheet game summaries (1871+)';
