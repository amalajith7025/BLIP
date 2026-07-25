CREATE TABLE findings (

    finding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    hypothesis_id UUID NOT NULL,

    finding_title VARCHAR(255) NOT NULL,

    finding_description TEXT NOT NULL,

    finding_type VARCHAR(50) NOT NULL DEFAULT 'OBSERVATION'
        CHECK (finding_type IN (
            'OBSERVATION',
            'ROOT_CAUSE',
            'INSIGHT',
            'RISK',
            'OPPORTUNITY',
            'CONCLUSION'
        )),

    confidence_score DECIMAL(5,2)
        CHECK (confidence_score BETWEEN 0 AND 100),

    created_by VARCHAR(20) NOT NULL DEFAULT 'USER'
        CHECK (created_by IN (
            'USER',
            'AI',
            'SYSTEM'
        )),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_findings_hypothesis
        FOREIGN KEY (hypothesis_id)
        REFERENCES hypotheses (hypothesis_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_findings_hypothesis
ON findings (hypothesis_id);

CREATE INDEX idx_findings_type
ON findings (finding_type);

CREATE INDEX idx_findings_confidence
ON findings (confidence_score);