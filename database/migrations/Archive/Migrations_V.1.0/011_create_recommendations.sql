CREATE TABLE recommendations (

    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    finding_id UUID NOT NULL,

    recommendation TEXT NOT NULL,

    expected_business_impact TEXT,

    priority VARCHAR(20) DEFAULT 'MEDIUM',

    implementation_status VARCHAR(30) DEFAULT 'PENDING',

    confidence_score DECIMAL(5,2),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_recommendation_finding
        FOREIGN KEY (finding_id)
        REFERENCES findings(finding_id)
        ON DELETE CASCADE
);