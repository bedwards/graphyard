-- Health Data Schema
-- Normalized schema for COVID-19 and other health datasets

CREATE SCHEMA IF NOT EXISTS health;

-- =============================================================================
-- COVID-19 Data (from OWID)
-- =============================================================================
CREATE TABLE IF NOT EXISTS health.covid_country_day (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    iso_code VARCHAR(10),                    -- Original ISO code from data
    location VARCHAR(100),                   -- Country/region name
    continent VARCHAR(50),
    date DATE NOT NULL,

    -- Cases
    total_cases BIGINT,
    new_cases INTEGER,
    new_cases_smoothed DECIMAL(12,3),
    total_cases_per_million DECIMAL(12,3),
    new_cases_per_million DECIMAL(12,3),
    new_cases_smoothed_per_million DECIMAL(12,3),

    -- Deaths
    total_deaths BIGINT,
    new_deaths INTEGER,
    new_deaths_smoothed DECIMAL(12,3),
    total_deaths_per_million DECIMAL(12,3),
    new_deaths_per_million DECIMAL(12,3),
    new_deaths_smoothed_per_million DECIMAL(12,3),

    -- ICU/Hospital
    icu_patients INTEGER,
    icu_patients_per_million DECIMAL(12,3),
    hosp_patients INTEGER,
    hosp_patients_per_million DECIMAL(12,3),
    weekly_icu_admissions DECIMAL(12,3),
    weekly_hosp_admissions DECIMAL(12,3),

    -- Testing
    total_tests BIGINT,
    new_tests INTEGER,
    total_tests_per_thousand DECIMAL(12,3),
    new_tests_per_thousand DECIMAL(12,3),
    new_tests_smoothed INTEGER,
    new_tests_smoothed_per_thousand DECIMAL(12,3),
    positive_rate DECIMAL(6,4),
    tests_per_case DECIMAL(12,3),

    -- Vaccinations
    total_vaccinations BIGINT,
    people_vaccinated BIGINT,
    people_fully_vaccinated BIGINT,
    total_boosters BIGINT,
    new_vaccinations INTEGER,
    new_vaccinations_smoothed INTEGER,
    total_vaccinations_per_hundred DECIMAL(8,3),
    people_vaccinated_per_hundred DECIMAL(8,3),
    people_fully_vaccinated_per_hundred DECIMAL(8,3),
    total_boosters_per_hundred DECIMAL(8,3),
    new_vaccinations_smoothed_per_million DECIMAL(12,3),

    -- Excess mortality
    excess_mortality DECIMAL(8,3),
    excess_mortality_cumulative DECIMAL(10,3),
    excess_mortality_cumulative_absolute DECIMAL(15,3),
    excess_mortality_cumulative_per_million DECIMAL(12,3),

    -- Reproduction rate
    reproduction_rate DECIMAL(6,3),

    -- Policy stringency
    stringency_index DECIMAL(6,3),

    -- Demographics (context)
    population BIGINT,
    population_density DECIMAL(12,3),
    median_age DECIMAL(5,2),
    aged_65_older DECIMAL(6,3),
    aged_70_older DECIMAL(6,3),
    gdp_per_capita DECIMAL(12,3),
    extreme_poverty DECIMAL(6,3),
    cardiovasc_death_rate DECIMAL(10,3),
    diabetes_prevalence DECIMAL(6,3),
    female_smokers DECIMAL(6,3),
    male_smokers DECIMAL(6,3),
    handwashing_facilities DECIMAL(6,3),
    hospital_beds_per_thousand DECIMAL(6,3),
    life_expectancy DECIMAL(6,3),
    human_development_index DECIMAL(5,3),

    UNIQUE(iso_code, date)
);

CREATE INDEX idx_covid_date ON health.covid_country_day(date);
CREATE INDEX idx_covid_country ON health.covid_country_day(country_id);
CREATE INDEX idx_covid_location ON health.covid_country_day(location);

-- =============================================================================
-- JHU COVID Time Series (simplified format)
-- =============================================================================
CREATE TABLE IF NOT EXISTS health.jhu_covid_timeseries (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES master.countries(id),
    province_state VARCHAR(200),
    country_region VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    date DATE NOT NULL,
    metric VARCHAR(20) NOT NULL,             -- 'confirmed', 'deaths', 'recovered'
    value BIGINT,
    UNIQUE(country_region, province_state, date, metric)
);

CREATE INDEX idx_jhu_date ON health.jhu_covid_timeseries(date);
CREATE INDEX idx_jhu_metric ON health.jhu_covid_timeseries(metric);

-- =============================================================================
-- Global Health Indicators (placeholder for WHO/CDC data)
-- =============================================================================
CREATE TABLE IF NOT EXISTS health.indicators (
    id SERIAL PRIMARY KEY,
    indicator_code VARCHAR(50) UNIQUE NOT NULL,
    indicator_name VARCHAR(500) NOT NULL,
    source VARCHAR(100),                     -- WHO, CDC, etc.
    unit VARCHAR(100),
    description TEXT
);

CREATE TABLE IF NOT EXISTS health.indicator_values (
    id SERIAL PRIMARY KEY,
    indicator_id INTEGER REFERENCES health.indicators(id),
    country_id INTEGER REFERENCES master.countries(id),
    year SMALLINT,
    value DECIMAL(20,6),
    UNIQUE(indicator_id, country_id, year)
);

COMMENT ON SCHEMA health IS 'Health datasets - COVID-19, WHO indicators, mortality data';
