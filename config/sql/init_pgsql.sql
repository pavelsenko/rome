CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name TEXT NOT NULL,
    project_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE functions (
    function_id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(project_id) ON DELETE CASCADE,
    function_name TEXT NOT NULL,
    function_code TEXT NOT NULL,
    embedding FLOAT[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX embedding_idx ON functions USING gin (embedding gin_trgm_ops);

-- Table to keep track of processed commits
CREATE TABLE commits (
    commit_id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(project_id) ON DELETE CASCADE,
    commit_hash TEXT UNIQUE NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP
);

-- This table is for potential duplicate or similar functions, storing references between functions
CREATE TABLE similar_functions (
    function_id INT REFERENCES functions(function_id) ON DELETE CASCADE,
    similar_function_id INT REFERENCES functions(function_id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    PRIMARY KEY (function_id, similar_function_id)
);
