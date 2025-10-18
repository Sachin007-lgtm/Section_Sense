-- Criminal Law Knowledge Base - PostgreSQL Schema
-- This script creates all tables in Supabase PostgreSQL

-- Drop existing tables if they exist (be careful in production!)
DROP TABLE IF EXISTS case_similarities CASCADE;
DROP TABLE IF EXISTS search_queries CASCADE;
DROP TABLE IF EXISTS law_amendments CASCADE;
DROP TABLE IF EXISTS case_citations CASCADE;
DROP TABLE IF EXISTS case_section_association CASCADE;
DROP TABLE IF EXISTS legal_cases CASCADE;
DROP TABLE IF EXISTS law_sections CASCADE;

-- Create law_sections table
CREATE TABLE law_sections (
    id SERIAL PRIMARY KEY,
    section_code VARCHAR(50) UNIQUE NOT NULL,
    section_number VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    punishment TEXT,
    fine_range VARCHAR(100),
    imprisonment_range VARCHAR(100),
    bailable VARCHAR(10),
    cognizable VARCHAR(10),
    compoundable VARCHAR(10),
    source VARCHAR(500),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for law_sections
CREATE INDEX idx_law_sections_section_code ON law_sections(section_code);
CREATE INDEX idx_law_sections_category ON law_sections(category);
CREATE INDEX idx_law_sections_section_number ON law_sections(section_number);

-- Create legal_cases table
CREATE TABLE legal_cases (
    id SERIAL PRIMARY KEY,
    case_number VARCHAR(100) UNIQUE NOT NULL,
    case_title VARCHAR(500) NOT NULL,
    petitioner VARCHAR(200),
    respondent VARCHAR(200),
    court VARCHAR(200) NOT NULL,
    bench VARCHAR(100),
    case_type VARCHAR(100),
    case_summary TEXT,
    facts TEXT,
    issues TEXT,
    arguments TEXT,
    judgment TEXT,
    verdict VARCHAR(100),
    filing_date TIMESTAMP,
    judgment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for legal_cases
CREATE INDEX idx_legal_cases_case_number ON legal_cases(case_number);
CREATE INDEX idx_legal_cases_court ON legal_cases(court);
CREATE INDEX idx_legal_cases_judgment_date ON legal_cases(judgment_date);

-- Create case_section_association table (many-to-many)
CREATE TABLE case_section_association (
    case_id INTEGER REFERENCES legal_cases(id) ON DELETE CASCADE,
    section_id INTEGER REFERENCES law_sections(id) ON DELETE CASCADE,
    PRIMARY KEY (case_id, section_id)
);

-- Create case_citations table
CREATE TABLE case_citations (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES legal_cases(id) ON DELETE CASCADE NOT NULL,
    citation_text VARCHAR(200) NOT NULL,
    citation_type VARCHAR(50),
    year INTEGER,
    volume VARCHAR(20),
    page VARCHAR(20)
);

CREATE INDEX idx_case_citations_case_id ON case_citations(case_id);

-- Create law_amendments table
CREATE TABLE law_amendments (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES law_sections(id) ON DELETE CASCADE NOT NULL,
    amendment_number VARCHAR(100),
    amendment_date TIMESTAMP,
    amendment_type VARCHAR(100),
    old_text TEXT,
    new_text TEXT,
    reason TEXT,
    source VARCHAR(500)
);

CREATE INDEX idx_law_amendments_section_id ON law_amendments(section_id);

-- Create search_queries table
CREATE TABLE search_queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    user_type VARCHAR(50),
    search_type VARCHAR(50),
    results_count INTEGER,
    execution_time FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

CREATE INDEX idx_search_queries_timestamp ON search_queries(timestamp);

-- Create case_similarities table
CREATE TABLE case_similarities (
    id SERIAL PRIMARY KEY,
    case1_id INTEGER REFERENCES legal_cases(id) ON DELETE CASCADE NOT NULL,
    case2_id INTEGER REFERENCES legal_cases(id) ON DELETE CASCADE NOT NULL,
    similarity_score FLOAT NOT NULL,
    similarity_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_case_pair UNIQUE (case1_id, case2_id)
);

-- Add comments to tables for documentation
COMMENT ON TABLE law_sections IS 'Stores Indian Penal Code sections and other law sections';
COMMENT ON TABLE legal_cases IS 'Stores legal cases and judgments';
COMMENT ON TABLE case_section_association IS 'Many-to-many relationship between cases and law sections';
COMMENT ON TABLE case_citations IS 'Stores citations for legal cases';
COMMENT ON TABLE law_amendments IS 'Tracks amendments to law sections';
COMMENT ON TABLE search_queries IS 'Analytics tracking for search queries';
COMMENT ON TABLE case_similarities IS 'Stores similarity scores between cases';

-- Create trigger to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_law_sections_modtime
    BEFORE UPDATE ON law_sections
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database schema created successfully!';
END $$;
