CREATE TABLE recommendations (

    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    finding_id UUID NOT NULL,

    recommendation_title VARCHAR(255) NOT NULL,

    recommendation_text TEXT NOT NULL,

    expected_business_impact TEXT,

    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM'
        CHECK (priority IN (
            'LOW',
            'MEDIUM',
            'HIGH',
            'CRITICAL'
        )),

    implementation_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (implementation_status IN (
            'PENDING',
            'IN_PROGRESS',
            'IMPLEMENTED',
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

    CONSTRAINT fk_recommendations_finding
        FOREIGN KEY (finding_id)
        REFERENCES findings (finding_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_recommendations_finding
ON recommendations (finding_id);

CREATE INDEX idx_recommendations_priority
ON recommendations (priority);

CREATE INDEX idx_recommendations_status
ON recommendations (implementation_status);

CREATE INDEX idx_recommendations_confidence
ON recommendations (confidence_score);