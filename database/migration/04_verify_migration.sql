# =============================================================================
# OBRAS – Verify migration on the homelab server
# Run this after 03_import_homelab.sh to confirm data integrity.
# Usage: psql -U postgres -d obras_db -f 04_verify_migration.sql
# =============================================================================

-- Row counts per table
\echo '=== Row counts ==='
SELECT
    relname              AS "table",
    n_live_tup::BIGINT   AS "rows (approx)"
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY relname;

-- Exact counts (slower, but accurate)
\echo ''
\echo '=== Exact row counts ==='
SELECT 'users'               AS "table", COUNT(*) AS rows FROM users
UNION ALL
SELECT 'projects',                        COUNT(*) FROM projects
UNION ALL
SELECT 'project_users',                   COUNT(*) FROM project_users
UNION ALL
SELECT 'accessories',                     COUNT(*) FROM accessories
UNION ALL
SELECT 'external_inspections',            COUNT(*) FROM external_inspections
UNION ALL
SELECT 'site_inspections',                COUNT(*) FROM site_inspections
UNION ALL
SELECT 'decommission_records',            COUNT(*) FROM decommission_records
UNION ALL
SELECT 'audit_logs',                      COUNT(*) FROM audit_logs
ORDER BY 1;

-- Check all ENUM types exist
\echo ''
\echo '=== ENUM types ==='
SELECT typname, array_agg(enumlabel ORDER BY enumsortorder) AS values
FROM pg_type
JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid
WHERE typname IN (
    'roleenum','projectstatusenum','brandenum','elementtypeenum',
    'usagestatusenum','inspectionstatusenum','externalinspectioncompanyenum',
    'colorperiodenum','siteinspectionresultenum','siteinspectioncompanyenum',
    'auditactionenum'
)
GROUP BY typname
ORDER BY typname;

-- FK integrity checks (should return 0 orphaned rows for each)
\echo ''
\echo '=== Foreign key integrity checks (all should be 0) ==='

SELECT 'projects -> users (created_by)' AS check_name,
       COUNT(*) AS orphans
FROM projects p
WHERE p.created_by IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = p.created_by)

UNION ALL

SELECT 'project_users -> projects', COUNT(*)
FROM project_users pu
WHERE NOT EXISTS (SELECT 1 FROM projects p WHERE p.id = pu.project_id)

UNION ALL

SELECT 'project_users -> users', COUNT(*)
FROM project_users pu
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = pu.user_id)

UNION ALL

SELECT 'accessories -> projects', COUNT(*)
FROM accessories a
WHERE NOT EXISTS (SELECT 1 FROM projects p WHERE p.id = a.project_id)

UNION ALL

SELECT 'external_inspections -> accessories', COUNT(*)
FROM external_inspections ei
WHERE NOT EXISTS (SELECT 1 FROM accessories a WHERE a.id = ei.accessory_id)

UNION ALL

SELECT 'site_inspections -> accessories', COUNT(*)
FROM site_inspections si
WHERE NOT EXISTS (SELECT 1 FROM accessories a WHERE a.id = si.accessory_id)

UNION ALL

SELECT 'decommission_records -> accessories', COUNT(*)
FROM decommission_records dr
WHERE NOT EXISTS (SELECT 1 FROM accessories a WHERE a.id = dr.accessory_id)

UNION ALL

SELECT 'audit_logs -> users', COUNT(*)
FROM audit_logs al
WHERE al.user_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = al.user_id);

-- Check admin user exists
\echo ''
\echo '=== Admin users ==='
SELECT id, email, full_name, role, is_active, created_at
FROM users
WHERE role = 'ADMIN'
ORDER BY created_at;

-- Check for soft-deleted records (informational)
\echo ''
\echo '=== Soft-deleted records (informational) ==='
SELECT 'users'              AS "table", COUNT(*) AS deleted_rows FROM users               WHERE deleted_at IS NOT NULL
UNION ALL
SELECT 'projects',           COUNT(*) FROM projects              WHERE deleted_at IS NOT NULL
UNION ALL
SELECT 'accessories',        COUNT(*) FROM accessories           WHERE deleted_at IS NOT NULL
UNION ALL
SELECT 'external_inspections',COUNT(*) FROM external_inspections WHERE deleted_at IS NOT NULL
UNION ALL
SELECT 'site_inspections',   COUNT(*) FROM site_inspections      WHERE deleted_at IS NOT NULL
UNION ALL
SELECT 'decommission_records',COUNT(*) FROM decommission_records WHERE deleted_at IS NOT NULL
ORDER BY 1;
