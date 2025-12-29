-- Master Schema: Cross-dataset entity resolution
-- This schema provides a single source of truth for entities (countries, etc.)
-- that appear across multiple datasets with different coding systems.

CREATE SCHEMA IF NOT EXISTS master;

-- =============================================================================
-- COUNTRIES: Master country table with canonical information
-- =============================================================================
CREATE TABLE IF NOT EXISTS master.countries (
    id SERIAL PRIMARY KEY,

    -- Canonical identifiers (ISO 3166-1)
    iso_alpha3 CHAR(3) UNIQUE NOT NULL,      -- ISO 3166-1 alpha-3 (USA, GBR, CHN)
    iso_alpha2 CHAR(2),                       -- ISO 3166-1 alpha-2 (US, GB, CN)
    iso_numeric SMALLINT,                     -- ISO 3166-1 numeric (840, 826, 156)

    -- Display name
    name VARCHAR(100) NOT NULL,
    name_formal VARCHAR(200),                 -- Official name

    -- Geographic classification
    region VARCHAR(100),                      -- World Bank region
    subregion VARCHAR(100),

    -- Status
    is_sovereign BOOLEAN DEFAULT TRUE,
    exists_from DATE,                         -- Date of independence/creation
    exists_until DATE,                        -- NULL if still exists
    successor_id INTEGER REFERENCES master.countries(id),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_countries_iso3 ON master.countries(iso_alpha3);
CREATE INDEX idx_countries_name ON master.countries(name);

-- =============================================================================
-- COUNTRY_CODES: Mapping table for all coding systems
-- =============================================================================
CREATE TABLE IF NOT EXISTS master.country_codes (
    id SERIAL PRIMARY KEY,
    country_id INTEGER NOT NULL REFERENCES master.countries(id) ON DELETE CASCADE,

    code_system VARCHAR(50) NOT NULL,        -- 'cow_alpha', 'cow_numeric', 'wdi', 'un', 'ucdp', etc.
    code_value VARCHAR(20) NOT NULL,         -- The actual code in that system

    -- Validity period (some codes change over time)
    valid_from DATE,
    valid_until DATE,

    UNIQUE(code_system, code_value, valid_from)
);

CREATE INDEX idx_country_codes_lookup ON master.country_codes(code_system, code_value);
CREATE INDEX idx_country_codes_country ON master.country_codes(country_id);

-- =============================================================================
-- CODE_SYSTEMS: Registry of all coding systems
-- =============================================================================
CREATE TABLE IF NOT EXISTS master.code_systems (
    id SERIAL PRIMARY KEY,
    system_code VARCHAR(50) UNIQUE NOT NULL,
    system_name VARCHAR(100) NOT NULL,
    source VARCHAR(200),
    description TEXT,
    example_code VARCHAR(20)
);

INSERT INTO master.code_systems (system_code, system_name, source, description, example_code) VALUES
    ('iso_alpha3', 'ISO 3166-1 Alpha-3', 'ISO', 'Three-letter country codes', 'USA'),
    ('iso_alpha2', 'ISO 3166-1 Alpha-2', 'ISO', 'Two-letter country codes', 'US'),
    ('iso_numeric', 'ISO 3166-1 Numeric', 'ISO', 'Three-digit numeric codes', '840'),
    ('cow_alpha', 'COW Alphabetic', 'Correlates of War', 'COW country abbreviations', 'USA'),
    ('cow_numeric', 'COW Numeric', 'Correlates of War', 'COW country codes (ccode)', '2'),
    ('wdi', 'World Bank WDI', 'World Bank', 'World Development Indicators codes', 'USA'),
    ('un_numeric', 'UN M49 Numeric', 'United Nations', 'UN numeric country codes', '840'),
    ('ucdp', 'UCDP Country ID', 'Uppsala', 'UCDP internal country identifiers', NULL),
    ('gwno', 'Gleditsch-Ward', 'Gleditsch & Ward', 'G&W country numbers', '2')
ON CONFLICT (system_code) DO NOTHING;

-- =============================================================================
-- HELPER FUNCTION: Resolve country ID from any code system
-- =============================================================================
CREATE OR REPLACE FUNCTION master.resolve_country(
    p_code_system VARCHAR,
    p_code_value VARCHAR,
    p_date DATE DEFAULT CURRENT_DATE
) RETURNS INTEGER AS $$
    SELECT country_id
    FROM master.country_codes
    WHERE code_system = p_code_system
      AND code_value = p_code_value
      AND (valid_from IS NULL OR valid_from <= p_date)
      AND (valid_until IS NULL OR valid_until >= p_date)
    LIMIT 1;
$$ LANGUAGE SQL STABLE;

-- =============================================================================
-- VIEW: All country codes pivoted for easy lookup
-- =============================================================================
CREATE OR REPLACE VIEW master.country_codes_wide AS
SELECT
    c.id,
    c.iso_alpha3,
    c.iso_alpha2,
    c.iso_numeric,
    c.name,
    c.region,
    MAX(CASE WHEN cc.code_system = 'cow_numeric' THEN cc.code_value END) AS cow_code,
    MAX(CASE WHEN cc.code_system = 'wdi' THEN cc.code_value END) AS wdi_code,
    MAX(CASE WHEN cc.code_system = 'un_numeric' THEN cc.code_value END) AS un_code
FROM master.countries c
LEFT JOIN master.country_codes cc ON c.id = cc.country_id
GROUP BY c.id, c.iso_alpha3, c.iso_alpha2, c.iso_numeric, c.name, c.region;

COMMENT ON SCHEMA master IS 'Cross-dataset entity resolution - single source of truth for countries, etc.';
COMMENT ON TABLE master.countries IS 'Master country table with canonical ISO codes and metadata';
COMMENT ON TABLE master.country_codes IS 'Maps countries to codes in various systems (COW, WDI, UN, etc.)';
