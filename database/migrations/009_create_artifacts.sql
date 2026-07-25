CREATE TABLE artifacts (

    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    question_id UUID NOT NULL,

    artifact_name VARCHAR(255) NOT NULL,

    artifact_type VARCHAR(100) NOT NULL,

    file_name VARCHAR(255),

    file_path TEXT,

    file_size BIGINT,

    mime_type VARCHAR(255),

    source VARCHAR(255),

    uploaded_by VARCHAR(255),

    description TEXT,

    upload_status VARCHAR(20) NOT NULL DEFAULT 'UPLOADED'
        CHECK (upload_status IN (
            'UPLOADED',
            'PROCESSING',
            'PROCESSED',
            'FAILED'
        )),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_artifacts_question
        FOREIGN KEY (question_id)
        REFERENCES business_questions (question_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_artifacts_question
ON artifacts (question_id);

CREATE INDEX idx_artifacts_type
ON artifacts (artifact_type);

CREATE INDEX idx_artifacts_status
ON artifacts (upload_status);