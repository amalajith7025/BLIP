CREATE TABLE hypothesis_evidence (

    hypothesis_id UUID NOT NULL,

    evidence_id UUID NOT NULL,

    relationship_type VARCHAR(30) NOT NULL,

    strength_score DECIMAL(5,2),

    notes TEXT,

    PRIMARY KEY (hypothesis_id, evidence_id),

    CONSTRAINT fk_he_hypothesis
        FOREIGN KEY (hypothesis_id)
        REFERENCES hypotheses(hypothesis_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_he_evidence
        FOREIGN KEY (evidence_id)
        REFERENCES evidence(evidence_id)
        ON DELETE CASCADE
);