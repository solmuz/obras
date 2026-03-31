-- =============================================================================
-- OBRAS - Sistema de Gestión de Accesorios de Izaje
-- PostgreSQL Schema — generated from SQLAlchemy models (v1.0)
-- Target: PostgreSQL 14+
-- Run this on the destination server BEFORE importing data.
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- ENUM TYPES
-- Drop in reverse order if re-running from scratch.
-- =============================================================================

DO $$ BEGIN
    CREATE TYPE roleenum AS ENUM ('ADMIN', 'INGENIERO_HSE', 'CONSULTA');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE projectstatusenum AS ENUM ('ACTIVO', 'INACTIVO');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE brandenum AS ENUM ('BRAND_1', 'BRAND_2', 'BRAND_3');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE elementtypeenum AS ENUM ('ESLINGAS', 'GRILLETES', 'GANCHOS', 'OTROS');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE usagestatusenum AS ENUM ('EN_USO', 'EN_STOCK', 'TAG_ROJO');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE inspectionstatusenum AS ENUM ('VIGENTE', 'VENCIDA');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE externalinspectioncompanyenum AS ENUM ('GEO', 'SBCIMAS', 'PREFA', 'BESSAC');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE colorperiodenum AS ENUM ('ENE_FEB', 'MAR_ABR', 'MAY_JUN', 'JUL_AGO', 'SEP_OCT', 'NOV_DIC');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE siteinspectionresultenum AS ENUM ('BUEN_ESTADO', 'MAL_ESTADO', 'OBSERVACIONES');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE siteinspectioncompanyenum AS ENUM ('GEO', 'SBCIMAS', 'PREFA', 'BESSAC');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE auditactionenum AS ENUM ('CREATE', 'UPDATE', 'DELETE');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- =============================================================================
-- TABLE: users
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255)    NOT NULL,
    full_name       VARCHAR(255)    NOT NULL,
    hashed_password VARCHAR(255)    NOT NULL,
    role            roleenum        NOT NULL DEFAULT 'CONSULTA',
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ     NULL,

    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS idx_users_email      ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users (deleted_at);

-- =============================================================================
-- TABLE: projects
-- =============================================================================

CREATE TABLE IF NOT EXISTS projects (
    id          UUID              PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255)      NOT NULL,
    description VARCHAR(1000)     NULL,
    status      projectstatusenum NOT NULL DEFAULT 'ACTIVO',
    start_date  TIMESTAMPTZ       NOT NULL,
    created_by  UUID              NULL REFERENCES users (id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ       NULL,

    CONSTRAINT uq_projects_name UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS idx_projects_name       ON projects (name);
CREATE INDEX IF NOT EXISTS idx_projects_deleted_at ON projects (deleted_at);

-- =============================================================================
-- TABLE: project_users  (many-to-many association)
-- =============================================================================

CREATE TABLE IF NOT EXISTS project_users (
    project_id        UUID        NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    user_id           UUID        NOT NULL REFERENCES users    (id) ON DELETE CASCADE,
    fecha_asignacion  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_remocion    TIMESTAMPTZ NULL,

    CONSTRAINT pk_project_users PRIMARY KEY (project_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_project_users_project_id ON project_users (project_id);
CREATE INDEX IF NOT EXISTS idx_project_users_user_id    ON project_users (user_id);

-- =============================================================================
-- TABLE: accessories
-- =============================================================================

CREATE TABLE IF NOT EXISTS accessories (
    -- Fixed / identifying fields
    id                       UUID             PRIMARY KEY DEFAULT gen_random_uuid(),
    code_internal            VARCHAR(50)      NOT NULL,
    element_type             elementtypeenum  NOT NULL,
    brand                    brandenum        NOT NULL,
    serial                   VARCHAR(255)     NOT NULL,
    material                 VARCHAR(255)     NOT NULL,
    capacity_vertical        VARCHAR(100)     NULL,
    capacity_choker          VARCHAR(100)     NULL,
    capacity_basket          VARCHAR(100)     NULL,
    length_m                 DOUBLE PRECISION NULL,
    diameter_inches          VARCHAR(50)      NULL,
    num_ramales              INTEGER          NULL,

    -- Mutable fields
    project_id               UUID             NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    status                   usagestatusenum  NOT NULL DEFAULT 'EN_USO',

    -- Photo storage paths
    photo_accessory          VARCHAR(500)     NULL,
    photo_manufacturer_label VARCHAR(500)     NULL,
    photo_provider_marking   VARCHAR(500)     NULL,

    -- Optimistic locking
    version                  INTEGER          NOT NULL DEFAULT 1,

    -- Timestamps / soft delete
    created_at               TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    deleted_at               TIMESTAMPTZ      NULL,

    CONSTRAINT uq_accessories_code_internal UNIQUE (code_internal)
);

CREATE INDEX IF NOT EXISTS idx_accessories_code_internal ON accessories (code_internal);
CREATE INDEX IF NOT EXISTS idx_accessories_project_id    ON accessories (project_id);
CREATE INDEX IF NOT EXISTS idx_accessories_deleted_at    ON accessories (deleted_at);

-- =============================================================================
-- TABLE: external_inspections
-- =============================================================================

CREATE TABLE IF NOT EXISTS external_inspections (
    id                   UUID                          PRIMARY KEY DEFAULT gen_random_uuid(),
    accessory_id         UUID                          NOT NULL REFERENCES accessories (id) ON DELETE CASCADE,

    -- Inspection data
    inspection_date      TIMESTAMPTZ                   NOT NULL,
    company              externalinspectioncompanyenum NOT NULL,
    company_responsible  VARCHAR(255)                  NOT NULL,
    final_criterion      VARCHAR(255)                  NOT NULL,

    -- Auto-calculated
    next_inspection_date TIMESTAMPTZ                   NOT NULL,
    status               inspectionstatusenum          NOT NULL DEFAULT 'VIGENTE',

    -- Files
    certificate_pdf      VARCHAR(500)                  NOT NULL,
    certificate_number   VARCHAR(100)                  NULL,

    -- Denormalized snapshot
    project_name         VARCHAR(255)                  NOT NULL,
    equipment_status     VARCHAR(50)                   NOT NULL,

    -- Optimistic locking
    version              INTEGER                       NOT NULL DEFAULT 1,

    -- Timestamps / soft delete
    created_at           TIMESTAMPTZ                   NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ                   NOT NULL DEFAULT NOW(),
    deleted_at           TIMESTAMPTZ                   NULL
);

CREATE INDEX IF NOT EXISTS idx_ext_insp_accessory_id         ON external_inspections (accessory_id);
CREATE INDEX IF NOT EXISTS idx_ext_insp_next_inspection_date ON external_inspections (next_inspection_date);
CREATE INDEX IF NOT EXISTS idx_ext_insp_deleted_at           ON external_inspections (deleted_at);

-- =============================================================================
-- TABLE: site_inspections
-- =============================================================================

CREATE TABLE IF NOT EXISTS site_inspections (
    id                   UUID                       PRIMARY KEY DEFAULT gen_random_uuid(),
    accessory_id         UUID                       NOT NULL REFERENCES accessories (id) ON DELETE CASCADE,

    -- Inspection data
    inspection_date      TIMESTAMPTZ                NOT NULL,
    final_criterion      siteinspectionresultenum   NOT NULL,
    inspector_name       VARCHAR(255)               NOT NULL,
    company              siteinspectioncompanyenum  NOT NULL,

    -- Auto-calculated
    color_period         colorperiodenum            NOT NULL,
    next_inspection_date TIMESTAMPTZ                NOT NULL,
    status               inspectionstatusenum       NOT NULL DEFAULT 'VIGENTE',

    -- Photo storage (PostgreSQL native array)
    photo_urls           VARCHAR(500)[]             NULL,

    -- Denormalized snapshot
    project_name         VARCHAR(255)               NOT NULL,
    equipment_status     VARCHAR(50)                NOT NULL,

    -- Optimistic locking
    version              INTEGER                    NOT NULL DEFAULT 1,

    -- Timestamps / soft delete
    created_at           TIMESTAMPTZ                NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ                NOT NULL DEFAULT NOW(),
    deleted_at           TIMESTAMPTZ                NULL
);

CREATE INDEX IF NOT EXISTS idx_site_insp_accessory_id         ON site_inspections (accessory_id);
CREATE INDEX IF NOT EXISTS idx_site_insp_next_inspection_date ON site_inspections (next_inspection_date);
CREATE INDEX IF NOT EXISTS idx_site_insp_color_period         ON site_inspections (color_period);
CREATE INDEX IF NOT EXISTS idx_site_insp_deleted_at           ON site_inspections (deleted_at);

-- =============================================================================
-- TABLE: decommission_records
-- =============================================================================

CREATE TABLE IF NOT EXISTS decommission_records (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    accessory_id      UUID         NOT NULL UNIQUE REFERENCES accessories (id) ON DELETE CASCADE,

    -- Decommission data
    decommission_date TIMESTAMPTZ  NOT NULL,
    reason            TEXT         NOT NULL,
    responsible_name  VARCHAR(255) NOT NULL,

    -- Photo storage
    photo_urls        VARCHAR(500)[] NULL,

    -- Timestamps / soft delete
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at        TIMESTAMPTZ  NULL
);

CREATE INDEX IF NOT EXISTS idx_decomm_accessory_id ON decommission_records (accessory_id);
CREATE INDEX IF NOT EXISTS idx_decomm_deleted_at   ON decommission_records (deleted_at);

-- =============================================================================
-- TABLE: audit_logs
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id                 UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID            NULL REFERENCES users (id) ON DELETE SET NULL,

    -- Affected entity
    entity_type        VARCHAR(50)     NOT NULL,
    entity_id          UUID            NOT NULL,

    -- Action
    action             auditactionenum NOT NULL,

    -- Change details
    old_values         JSONB           NULL,
    new_values         JSONB           NULL,
    change_description TEXT            NULL,

    -- When
    created_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_user_id     ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity_type ON audit_logs (entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_entity_id   ON audit_logs (entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_action      ON audit_logs (action);
CREATE INDEX IF NOT EXISTS idx_audit_created_at  ON audit_logs (created_at);

-- =============================================================================
-- UPDATED_AT trigger function (reusable for all tables)
-- =============================================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DO $$ DECLARE t TEXT;
BEGIN
    FOR t IN SELECT unnest(ARRAY[
        'users', 'projects', 'accessories',
        'external_inspections', 'site_inspections', 'decommission_records'
    ]) LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS trg_%s_updated_at ON %I;
             CREATE TRIGGER trg_%s_updated_at
             BEFORE UPDATE ON %I
             FOR EACH ROW EXECUTE FUNCTION set_updated_at();',
            t, t, t, t
        );
    END LOOP;
END $$;

-- =============================================================================
-- DEFAULT ADMIN USER
-- Password: Admin1234!  (bcrypt hash — change on first login)
-- =============================================================================

INSERT INTO users (id, email, full_name, hashed_password, role, is_active)
VALUES (
    gen_random_uuid(),
    'admin@obras.local',
    'Administrador',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqzqC7bYBiI.qEuKl9kBqam',
    'ADMIN',
    TRUE
)
ON CONFLICT (email) DO NOTHING;
