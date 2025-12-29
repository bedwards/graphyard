-- Conflict Data Schemas
-- Normalized schemas for UCDP, Correlates of War, Political Terror Scale, and Iraq Body Count

-- =============================================================================
-- SCHEMA: UCDP (Uppsala Conflict Data Program)
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS ucdp;

-- Conflicts (armed conflicts)
CREATE TABLE IF NOT EXISTS ucdp.conflicts (
    id SERIAL PRIMARY KEY,
    conflict_id INTEGER UNIQUE NOT NULL,     -- UCDP conflict_new_id
    conflict_dset_id INTEGER,                -- Legacy ID
    name VARCHAR(500) NOT NULL,
    type_of_violence SMALLINT NOT NULL,      -- 1=state-based, 2=non-state, 3=one-sided
    start_date DATE,
    end_date DATE,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Actors (parties to conflicts)
CREATE TABLE IF NOT EXISTS ucdp.actors (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER UNIQUE NOT NULL,        -- side_a_new_id or side_b_new_id
    actor_dset_id INTEGER,
    name VARCHAR(500) NOT NULL,
    actor_type VARCHAR(50),                  -- government, rebel group, etc.
    country_id INTEGER REFERENCES master.countries(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dyads (pairs of actors in conflict)
CREATE TABLE IF NOT EXISTS ucdp.dyads (
    id SERIAL PRIMARY KEY,
    dyad_id INTEGER UNIQUE NOT NULL,         -- dyad_new_id
    dyad_dset_id INTEGER,
    name VARCHAR(500),
    conflict_id INTEGER REFERENCES ucdp.conflicts(id),
    side_a_id INTEGER REFERENCES ucdp.actors(id),
    side_b_id INTEGER REFERENCES ucdp.actors(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GED Events (Georeferenced Event Dataset) - the main event-level data
CREATE TABLE IF NOT EXISTS ucdp.ged_events (
    id SERIAL PRIMARY KEY,
    event_id INTEGER UNIQUE NOT NULL,        -- UCDP id
    relid INTEGER,
    year SMALLINT NOT NULL,
    active_year BOOLEAN,
    type_of_violence SMALLINT NOT NULL,
    conflict_id INTEGER REFERENCES ucdp.conflicts(id),
    dyad_id INTEGER REFERENCES ucdp.dyads(id),
    side_a_id INTEGER REFERENCES ucdp.actors(id),
    side_b_id INTEGER REFERENCES ucdp.actors(id),

    -- Location
    country_id INTEGER REFERENCES master.countries(id),
    adm_1 VARCHAR(200),
    adm_2 VARCHAR(200),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    where_prec SMALLINT,
    where_description TEXT,

    -- Dates
    date_start DATE,
    date_end DATE,
    date_prec SMALLINT,

    -- Casualties
    deaths_a INTEGER,
    deaths_b INTEGER,
    deaths_civilians INTEGER,
    deaths_unknown INTEGER,
    best_estimate INTEGER,                   -- Best total estimate
    low_estimate INTEGER,
    high_estimate INTEGER,

    -- Sources
    source_article TEXT,
    source_office TEXT,
    source_date DATE,
    number_of_sources SMALLINT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ged_year ON ucdp.ged_events(year);
CREATE INDEX idx_ged_country ON ucdp.ged_events(country_id);
CREATE INDEX idx_ged_conflict ON ucdp.ged_events(conflict_id);
CREATE INDEX idx_ged_location ON ucdp.ged_events(latitude, longitude);

-- Battle-related deaths (annual aggregates)
CREATE TABLE IF NOT EXISTS ucdp.battle_deaths (
    id SERIAL PRIMARY KEY,
    conflict_id INTEGER REFERENCES ucdp.conflicts(id),
    dyad_id INTEGER REFERENCES ucdp.dyads(id),
    year SMALLINT NOT NULL,
    bd_best INTEGER,
    bd_low INTEGER,
    bd_high INTEGER,
    UNIQUE(dyad_id, year)
);

-- One-sided violence
CREATE TABLE IF NOT EXISTS ucdp.one_sided_violence (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER REFERENCES ucdp.actors(id),
    year SMALLINT NOT NULL,
    country_id INTEGER REFERENCES master.countries(id),
    best_estimate INTEGER,
    low_estimate INTEGER,
    high_estimate INTEGER,
    is_government_actor BOOLEAN,
    UNIQUE(actor_id, year, country_id)
);

COMMENT ON SCHEMA ucdp IS 'Uppsala Conflict Data Program - armed conflict events 1946-present';

-- =============================================================================
-- SCHEMA: COW (Correlates of War)
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS cow;

-- Wars (unified table for all war types)
CREATE TABLE IF NOT EXISTS cow.wars (
    id SERIAL PRIMARY KEY,
    war_num INTEGER NOT NULL,
    war_name VARCHAR(200) NOT NULL,
    war_type SMALLINT NOT NULL,              -- 1=inter-state, 2-3=extra-state, 4-7=intra-state, 8-9=non-state
    war_type_name VARCHAR(50),
    start_year SMALLINT,
    start_month SMALLINT,
    start_day SMALLINT,
    end_year SMALLINT,
    end_month SMALLINT,
    end_day SMALLINT,
    initiator SMALLINT,
    outcome SMALLINT,
    trans_from INTEGER,                      -- Transformed from war #
    trans_to INTEGER,                        -- Transformed to war #
    where_fought SMALLINT,
    total_battle_deaths INTEGER,
    version VARCHAR(10),
    UNIQUE(war_num, war_type)
);

-- War participants
CREATE TABLE IF NOT EXISTS cow.war_participants (
    id SERIAL PRIMARY KEY,
    war_id INTEGER REFERENCES cow.wars(id),
    country_id INTEGER REFERENCES master.countries(id),
    cow_code INTEGER,                        -- Original COW ccode
    state_name VARCHAR(100),
    side SMALLINT,                           -- 1 or 2
    start_year SMALLINT,
    start_month SMALLINT,
    start_day SMALLINT,
    end_year SMALLINT,
    end_month SMALLINT,
    end_day SMALLINT,
    initiator BOOLEAN,
    outcome SMALLINT,
    battle_deaths INTEGER,
    UNIQUE(war_id, cow_code, start_year)
);

-- Militarized Interstate Disputes (MIDs)
CREATE TABLE IF NOT EXISTS cow.mids (
    id SERIAL PRIMARY KEY,
    disp_num INTEGER UNIQUE NOT NULL,        -- Dispute number
    start_year SMALLINT,
    start_month SMALLINT,
    start_day SMALLINT,
    end_year SMALLINT,
    end_month SMALLINT,
    end_day SMALLINT,
    outcome SMALLINT,
    settle SMALLINT,
    fatality SMALLINT,                       -- Fatality level
    fatality_precise INTEGER,
    max_duration INTEGER,
    min_duration INTEGER,
    host_lev SMALLINT,                       -- Highest hostility level
    recip BOOLEAN,
    num_states SMALLINT,
    version VARCHAR(10)
);

-- MID Participants
CREATE TABLE IF NOT EXISTS cow.mid_participants (
    id SERIAL PRIMARY KEY,
    mid_id INTEGER REFERENCES cow.mids(id),
    country_id INTEGER REFERENCES master.countries(id),
    cow_code INTEGER,
    state_name VARCHAR(100),
    start_year SMALLINT,
    end_year SMALLINT,
    side_a BOOLEAN,
    rev_state BOOLEAN,
    rev_type1 SMALLINT,
    fatality SMALLINT,
    host_lev SMALLINT,
    orig BOOLEAN                             -- Originator
);

-- National Material Capabilities (CINC scores)
CREATE TABLE IF NOT EXISTS cow.national_capabilities (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    cow_code INTEGER,
    state_abbrev VARCHAR(10),
    year SMALLINT NOT NULL,

    -- Raw capability components
    milex BIGINT,                            -- Military expenditure
    milper INTEGER,                          -- Military personnel
    irst INTEGER,                            -- Iron/steel production
    pec INTEGER,                             -- Primary energy consumption
    tpop BIGINT,                             -- Total population
    upop BIGINT,                             -- Urban population

    -- Composite index
    cinc DECIMAL(10,8),                      -- Composite Index of National Capability

    version VARCHAR(10),
    UNIQUE(cow_code, year)
);

CREATE INDEX idx_nmc_year ON cow.national_capabilities(year);
CREATE INDEX idx_nmc_country ON cow.national_capabilities(country_id);

-- Alliances
CREATE TABLE IF NOT EXISTS cow.alliances (
    id SERIAL PRIMARY KEY,
    alliance_id INTEGER NOT NULL,
    alliance_name VARCHAR(200),
    start_year SMALLINT,
    end_year SMALLINT,
    alliance_type SMALLINT,                  -- 1=defense, 2=neutrality, 3=entente
    version VARCHAR(10)
);

-- Alliance members
CREATE TABLE IF NOT EXISTS cow.alliance_members (
    id SERIAL PRIMARY KEY,
    alliance_id INTEGER REFERENCES cow.alliances(id),
    country_id INTEGER REFERENCES master.countries(id),
    cow_code INTEGER,
    state_name VARCHAR(100),
    start_year SMALLINT,
    end_year SMALLINT
);

COMMENT ON SCHEMA cow IS 'Correlates of War - wars, disputes, capabilities 1816-present';

-- =============================================================================
-- SCHEMA: PTS (Political Terror Scale)
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS pts;

CREATE TABLE IF NOT EXISTS pts.country_year_scores (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    country_name VARCHAR(100),
    year SMALLINT NOT NULL,

    -- Codes (for reference/debugging)
    cow_code_alpha VARCHAR(10),
    cow_code_numeric INTEGER,
    wb_code VARCHAR(10),
    un_code INTEGER,
    region VARCHAR(50),

    -- PTS scores (1-5 scale, higher = worse)
    pts_amnesty SMALLINT,                    -- Amnesty International score
    pts_state_dept SMALLINT,                 -- US State Department score
    pts_hrw SMALLINT,                        -- Human Rights Watch score

    -- NA status flags
    na_status_amnesty SMALLINT,
    na_status_state_dept SMALLINT,
    na_status_hrw SMALLINT,

    UNIQUE(country_id, year)
);

CREATE INDEX idx_pts_year ON pts.country_year_scores(year);
CREATE INDEX idx_pts_country ON pts.country_year_scores(country_id);

COMMENT ON SCHEMA pts IS 'Political Terror Scale - human rights violations 1976-present';

-- =============================================================================
-- SCHEMA: IBC (Iraq Body Count)
-- =============================================================================
CREATE SCHEMA IF NOT EXISTS ibc;

CREATE TABLE IF NOT EXISTS ibc.incidents (
    id SERIAL PRIMARY KEY,
    ibc_id VARCHAR(50) UNIQUE,               -- IBC incident identifier
    start_date DATE,
    end_date DATE,
    location VARCHAR(500),
    target VARCHAR(500),
    weapons TEXT,
    deaths_min INTEGER,
    deaths_max INTEGER,
    sources TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ibc.individuals (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER REFERENCES ibc.incidents(id),
    name VARCHAR(200),
    age INTEGER,
    sex CHAR(1),
    civilian_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ibc_date ON ibc.incidents(start_date);

COMMENT ON SCHEMA ibc IS 'Iraq Body Count - documented civilian casualties 2003-2017';
