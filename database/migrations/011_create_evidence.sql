CREATE TABLE evidence (

    evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    fact_id UUID NOT NULL,

    evidence_text TEXT NOT NULL,

    evidence_type VARCHAR(50)
        CHECK (evidence_type IN (
            'QUANTITATIVE',
            'QUALITATIVE',
            'DOCUMENTARY',
            'OBSERVATIONAL',
            'INTERVIEW',
            'SYSTEM_LOG',
            'OTHER'
        )),

    evidence_quality VARCHAR(20) NOT NULL DEFAULT 'MEDIUM'
        CHECK (evidence_quality IN (
            'LOW',
            'MEDIUM',
            'HIGH'
        )),

    confidence_score DECIMAL(5,2)
        CHECK (confidence_score BETWEEN 0 AND 100),

    extracted_by VARCHAR(20) NOT NULL DEFAULT 'AI'
        CHECK (extracted_by IN (
            'AI',
            'USER',
            'SYSTEM'
        )),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_evidence_fact
        FOREIGN KEY (fact_id)
        REFERENCES facts (fact_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_evidence_fact
ON evidence (fact_id);

CREATE INDEX idx_evidence_type
ON evidence (evidence_type);

CREATE INDEX idx_evidence_quality
ON evidence (evidence_quality);