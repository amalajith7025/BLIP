CREATE TABLE evidence (

    evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    artifact_id UUID NOT NULL,

    evidence_text TEXT NOT NULL,

    evidence_type VARCHAR(50),

    page_number INTEGER,

    source_location TEXT,

    evidence_quality VARCHAR(20) DEFAULT 'MEDIUM',

    confidence_score DECIMAL(5,2),

    extracted_by VARCHAR(20) DEFAULT 'AI',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_evidence_artifact
        FOREIGN KEY (artifact_id)
        REFERENCES artifacts(artifact_id)
        ON DELETE CASCADE
);