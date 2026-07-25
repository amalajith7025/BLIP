CREATE TABLE hypotheses (

    hypothesis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    question_id UUID NOT NULL,

    hypothesis TEXT NOT NULL,

    rationale TEXT,

    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    confidence_score DECIMAL(5,2),

    created_by VARCHAR(20) NOT NULL DEFAULT 'USER',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_hypothesis_question
        FOREIGN KEY (question_id)
        REFERENCES business_questions(question_id)
        ON DELETE CASCADE
);