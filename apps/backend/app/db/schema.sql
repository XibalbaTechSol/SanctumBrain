-- PARA Database Schema for Sanctum Brain
-- Optimized for PostgreSQL

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    goal TEXT,
    deadline TIMESTAMP,
    status VARCHAR(50) DEFAULT 'ACTIVE', -- 'ACTIVE', 'COMPLETED', 'ON_HOLD'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    responsibility_level INT DEFAULT 1, -- Higher is more important
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content_type VARCHAR(50) NOT NULL, -- 'DOC', 'LINK', 'CODE', 'MEDIA', 'NOTE'
    content_payload JSONB,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS archives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_id UUID NOT NULL,
    original_type VARCHAR(50) NOT NULL, -- 'PROJECT', 'AREA', 'RESOURCE'
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_resources_tags ON resources USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_archives_original_id ON archives(original_id);
