CREATE TABLE hypotheses (

    hypothesis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    question_id UUID NOT NULL,

    hypothesis_statement TEXT NOT NULL,

    rationale TEXT,

    status VARCHAR(30) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN (
            'PENDING',
            'SUPPORTED',
            'PARTIALLY_SUPPORTED',
            'REJECTED'
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

    CONSTRAINT fk_hypotheses_question
        FOREIGN KEY (question_id)
        REFERENCES business_questions (question_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_hypotheses_question
ON hypotheses (question_id);

CREATE INDEX idx_hypotheses_status
ON hypotheses (status);

CREATE INDEX idx_hypotheses_confidence
ON hypotheses (confidence_score);