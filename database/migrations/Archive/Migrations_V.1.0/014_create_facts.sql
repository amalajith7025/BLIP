CREATE TABLE facts (

    fact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    artifact_id UUID NOT NULL,

    fact_text TEXT NOT NULL,

    fact_type VARCHAR(100),

    source_location TEXT,

    confidence_score NUMERIC(5,2),

    extracted_by VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (artifact_id)

    REFERENCES artifacts(artifact_id)

    ON DELETE CASCADE
);