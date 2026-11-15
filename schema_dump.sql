-- 1. Source Metadata Table
CREATE TABLE IF NOT EXISTS source (
    source_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    base_url VARCHAR(255)
);

-- 2. Country Metadata Table
CREATE TABLE IF NOT EXISTS country (
    country_code VARCHAR(3) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    income_group VARCHAR(50)
);

-- 3. Indicator Metadata Table
CREATE TABLE IF NOT EXISTS indicator (
    indicator_id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    unit VARCHAR(50),
    source_id INT REFERENCES source(source_id) ON DELETE CASCADE
);

-- 4. Central Observations Fact Table
CREATE TABLE IF NOT EXISTS observation (
    observation_id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(3) REFERENCES country(country_code) ON DELETE CASCADE,
    indicator_id INT REFERENCES indicator(indicator_id) ON DELETE CASCADE,
    year INT NOT NULL,
    sex VARCHAR(10) DEFAULT 'BTSX',
    value NUMERIC(15, 4),
    is_outlier BOOLEAN DEFAULT FALSE,
    rehab_coverage_index NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_country_indicator_year_sex UNIQUE (country_code, indicator_id, year, sex)
);

-- 5. Import Audit Log Table
CREATE TABLE IF NOT EXISTS import_log (
    log_id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_imported INT DEFAULT 0,
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Query Optimization
CREATE INDEX IF NOT EXISTS idx_obs_country_year ON observation(country_code, year);
CREATE INDEX IF NOT EXISTS idx_obs_indicator ON observation(indicator_id);