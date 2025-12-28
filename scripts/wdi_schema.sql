-- WDI Normalized Database Schema
-- Database: graphyard

-- =============================================================================
-- Reference Tables (dimension tables)
-- =============================================================================

-- Indicators (from WDICSV - source of truth for names)
CREATE TABLE IF NOT EXISTS indicators (
    indicator_code VARCHAR(50) PRIMARY KEY,
    indicator_name TEXT NOT NULL,
    topic VARCHAR(200),
    short_definition TEXT,
    long_definition TEXT,
    unit_of_measure VARCHAR(100),
    periodicity VARCHAR(50),
    aggregation_method VARCHAR(100),
    source TEXT,
    license_type VARCHAR(50)
);

-- Entity types (country vs various aggregates)
CREATE TABLE IF NOT EXISTS entity_types (
    entity_type VARCHAR(50) PRIMARY KEY,
    description TEXT,
    is_country BOOLEAN NOT NULL DEFAULT FALSE
);

-- All entities (countries + aggregates)
CREATE TABLE IF NOT EXISTS entities (
    entity_code VARCHAR(10) PRIMARY KEY,
    entity_name VARCHAR(200) NOT NULL,
    entity_type VARCHAR(50) NOT NULL REFERENCES entity_types(entity_type),
    long_name VARCHAR(300),
    currency_unit VARCHAR(100),
    region VARCHAR(100),           -- NULL for aggregates
    income_group VARCHAR(50),      -- NULL for some aggregates
    special_notes TEXT
);

-- =============================================================================
-- Fact Tables (separated by entity type to avoid mixing)
-- =============================================================================

-- Country-level observations (the main table)
CREATE TABLE IF NOT EXISTS country_data (
    id BIGSERIAL PRIMARY KEY,
    entity_code VARCHAR(10) NOT NULL REFERENCES entities(entity_code),
    indicator_code VARCHAR(50) NOT NULL REFERENCES indicators(indicator_code),
    year SMALLINT NOT NULL,
    value DOUBLE PRECISION,
    UNIQUE (entity_code, indicator_code, year)
);

-- World aggregate observations
CREATE TABLE IF NOT EXISTS world_data (
    id BIGSERIAL PRIMARY KEY,
    indicator_code VARCHAR(50) NOT NULL REFERENCES indicators(indicator_code),
    year SMALLINT NOT NULL,
    value DOUBLE PRECISION,
    UNIQUE (indicator_code, year)
);

-- Geographic region observations
CREATE TABLE IF NOT EXISTS region_geo_data (
    id BIGSERIAL PRIMARY KEY,
    entity_code VARCHAR(10) NOT NULL REFERENCES entities(entity_code),
    indicator_code VARCHAR(50) NOT NULL REFERENCES indicators(indicator_code),
    year SMALLINT NOT NULL,
    value DOUBLE PRECISION,
    UNIQUE (entity_code, indicator_code, year)
);

-- Income group observations
CREATE TABLE IF NOT EXISTS income_data (
    id BIGSERIAL PRIMARY KEY,
    entity_code VARCHAR(10) NOT NULL REFERENCES entities(entity_code),
    indicator_code VARCHAR(50) NOT NULL REFERENCES indicators(indicator_code),
    year SMALLINT NOT NULL,
    value DOUBLE PRECISION,
    UNIQUE (entity_code, indicator_code, year)
);

-- Lending category observations
CREATE TABLE IF NOT EXISTS lending_data (
    id BIGSERIAL PRIMARY KEY,
    entity_code VARCHAR(10) NOT NULL REFERENCES entities(entity_code),
    indicator_code VARCHAR(50) NOT NULL REFERENCES indicators(indicator_code),
    year SMALLINT NOT NULL,
    value DOUBLE PRECISION,
    UNIQUE (entity_code, indicator_code, year)
);

-- Other aggregate observations (demographic, small_states, political, dev_status, etc.)
CREATE TABLE IF NOT EXISTS other_aggregate_data (
    id BIGSERIAL PRIMARY KEY,
    entity_code VARCHAR(10) NOT NULL REFERENCES entities(entity_code),
    indicator_code VARCHAR(50) NOT NULL REFERENCES indicators(indicator_code),
    year SMALLINT NOT NULL,
    value DOUBLE PRECISION,
    aggregate_type VARCHAR(50) NOT NULL,  -- demographic, small_states, political, etc.
    UNIQUE (entity_code, indicator_code, year)
);

-- =============================================================================
-- Indexes for query performance
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_country_data_entity ON country_data(entity_code);
CREATE INDEX IF NOT EXISTS idx_country_data_indicator ON country_data(indicator_code);
CREATE INDEX IF NOT EXISTS idx_country_data_year ON country_data(year);
CREATE INDEX IF NOT EXISTS idx_country_data_entity_year ON country_data(entity_code, year);

CREATE INDEX IF NOT EXISTS idx_world_data_indicator ON world_data(indicator_code);
CREATE INDEX IF NOT EXISTS idx_world_data_year ON world_data(year);

CREATE INDEX IF NOT EXISTS idx_region_geo_data_entity ON region_geo_data(entity_code);
CREATE INDEX IF NOT EXISTS idx_region_geo_data_year ON region_geo_data(year);

CREATE INDEX IF NOT EXISTS idx_income_data_entity ON income_data(entity_code);
CREATE INDEX IF NOT EXISTS idx_income_data_year ON income_data(year);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_region ON entities(region);

-- =============================================================================
-- Seed entity types
-- =============================================================================

INSERT INTO entity_types (entity_type, description, is_country) VALUES
    ('country', 'Actual country with geographic region', TRUE),
    ('world', 'Global aggregate (WLD)', FALSE),
    ('region_geo', 'Main World Bank geographic regions', FALSE),
    ('region_geo_sub', 'Sub-regional aggregates', FALSE),
    ('region_geo_exhi', 'Geographic regions excluding high income', FALSE),
    ('income', 'Income group aggregates', FALSE),
    ('lending', 'Lending category aggregates (IDA/IBRD)', FALSE),
    ('region_lending', 'Region + Lending combinations', FALSE),
    ('demographic', 'Demographic dividend stages', FALSE),
    ('small_states', 'Small state groupings', FALSE),
    ('political', 'Political/economic groupings', FALSE),
    ('dev_status', 'Development/fragility status groupings', FALSE),
    ('unknown_aggregate', 'Unclassified aggregate', FALSE)
ON CONFLICT (entity_type) DO NOTHING;
