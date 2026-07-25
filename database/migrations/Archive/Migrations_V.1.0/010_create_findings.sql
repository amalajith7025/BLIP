CREATE TABLE findings (

    finding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    hypothesis_id UUID NOT NULL,

    finding_title VARCHAR(255) NOT NULL,

    finding_description TEXT NOT NULL,

    confidence_score DECIMAL(5,2),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_finding_hypothesis
        FOREIGN KEY (hypothesis_id)
        REFERENCES hypotheses(hypothesis_id)
        ON DELETE CASCADE
);