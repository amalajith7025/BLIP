CREATE TABLE facts (

    fact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    artifact_id UUID NOT NULL,

    fact_text TEXT NOT NULL,

    fact_category VARCHAR(50)
        CHECK (fact_category IN (
            'METRIC',
            'OBSERVATION',
            'POLICY',
            'PROCEDURE',
            'COMPLAINT',
            'CUSTOMER_FEEDBACK',
            'EMPLOYEE_FEEDBACK',
            'FINANCIAL',
            'OPERATIONAL',
            'RISK',
            'OPPORTUNITY',
            'OTHER'
        )),

    fact_type VARCHAR(100),

    source_location TEXT,

    page_number INTEGER,

    confidence_score DECIMAL(5,2)
        CHECK (confidence_score BETWEEN 0 AND 100),

    extracted_by VARCHAR(20) NOT NULL DEFAULT 'AI'
        CHECK (extracted_by IN ('AI', 'USER', 'SYSTEM')),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_facts_artifact
        FOREIGN KEY (artifact_id)
        REFERENCES artifacts (artifact_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_facts_artifact
ON facts (artifact_id);

CREATE INDEX idx_facts_category
ON facts (fact_category);

CREATE INDEX idx_facts_type
ON facts (fact_type);