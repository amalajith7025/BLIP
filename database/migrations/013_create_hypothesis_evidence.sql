CREATE TABLE hypothesis_evidence (

    hypothesis_id UUID NOT NULL,

    evidence_id UUID NOT NULL,

    relationship_type VARCHAR(20) NOT NULL
        CHECK (relationship_type IN (
            'SUPPORTS',
            'CONTRADICTS',
            'NEUTRAL'
        )),

    strength_score DECIMAL(5,2)
        CHECK (strength_score BETWEEN 0 AND 100),

    notes TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (hypothesis_id, evidence_id),

    CONSTRAINT fk_hypothesis_evidence_hypothesis
        FOREIGN KEY (hypothesis_id)
        REFERENCES hypotheses (hypothesis_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_hypothesis_evidence_evidence
        FOREIGN KEY (evidence_id)
        REFERENCES evidence (evidence_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_hypothesis_evidence_hypothesis
ON hypothesis_evidence (hypothesis_id);

CREATE INDEX idx_hypothesis_evidence_evidence
ON hypothesis_evidence (evidence_id);

CREATE INDEX idx_hypothesis_evidence_relationship
ON hypothesis_evidence (relationship_type);