CREATE TABLE business_questions (

    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    investigation_id UUID NOT NULL,

    question_text TEXT NOT NULL,

    question_objective TEXT,

    description TEXT,

    status VARCHAR(20) NOT NULL DEFAULT 'OPEN'
        CHECK (status IN (
            'OPEN',
            'IN_PROGRESS',
            'ANSWERED',
            'CLOSED'
        )),

    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM'
        CHECK (priority IN (
            'LOW',
            'MEDIUM',
            'HIGH',
            'CRITICAL'
        )),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_business_questions_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigations (investigation_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_business_questions_investigation
ON business_questions (investigation_id);

CREATE INDEX idx_business_questions_status
ON business_questions (status);

CREATE INDEX idx_business_questions_priority
ON business_questions (priority);