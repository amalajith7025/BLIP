
CREATE TABLE artifacts (

    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    question_id UUID NOT NULL,

    artifact_name VARCHAR(255) NOT NULL,

    artifact_type VARCHAR(100),

    description TEXT,

    source VARCHAR(255),

    uploaded_by VARCHAR(255),

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_artifact_question
        FOREIGN KEY (question_id)
        REFERENCES business_questions(question_id)
        ON DELETE CASCADE
);