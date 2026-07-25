CREATE TABLE business_questions (

    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    investigation_id UUID NOT NULL,

    question TEXT NOT NULL,

    objective TEXT,

    status VARCHAR(20) DEFAULT 'OPEN',

    priority VARCHAR(20) DEFAULT 'MEDIUM',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_question_investigation
        FOREIGN KEY (investigation_id)
        REFERENCES investigations(investigation_id)
        ON DELETE CASCADE
);