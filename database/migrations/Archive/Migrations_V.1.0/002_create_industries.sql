CREATE TABLE industries (
    industry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    industry_name VARCHAR(100) NOT NULL UNIQUE,
    industry_code VARCHAR(20),

    description TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);