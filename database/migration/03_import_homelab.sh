#!/usr/bin/env bash
# =============================================================================
# OBRAS – Import data on the DESTINATION homelab server (Linux/Docker)
# Usage: bash 03_import_homelab.sh [path/to/export_dir]
#
# Requires: psql and pg_restore in PATH
# Must be run on (or from) the homelab server.
# =============================================================================

set -euo pipefail

# ---------- DESTINATION connection -------------------------------------------
DST_HOST="${PGHOST:-localhost}"
DST_PORT="${PGPORT:-5432}"
DST_DB="${PGDATABASE:-obras_db}"
DST_USER="${PGUSER:-postgres}"
export PGPASSWORD="${PGPASSWORD:-changeme}"   # override via env var

# ---------- Locate export directory ------------------------------------------
EXPORT_DIR="${1:-$(dirname "$0")/export}"
if [[ ! -d "$EXPORT_DIR" ]]; then
    echo "ERROR: Export directory not found: $EXPORT_DIR"
    echo "Usage: bash $0 /path/to/export_YYYYMMDD_HHmmss"
    exit 1
fi

SCHEMA_SQL="$EXPORT_DIR/schema_only.sql"
DATA_SQL="$EXPORT_DIR/data_inserts.sql"
FULL_DUMP="$EXPORT_DIR/full_dump.pgdump"
OBRA_SCHEMA="$(dirname "$0")/01_schema_postgresql.sql"

echo "=== OBRAS homelab import ==="
echo "Destination : $DST_USER@$DST_HOST:$DST_PORT/$DST_DB"
echo "Export dir  : $EXPORT_DIR"
echo ""

# ---------- 1. Create database if it doesn't exist ---------------------------
echo "[1/4] Ensuring database exists..."
psql \
    --host="$DST_HOST" --port="$DST_PORT" \
    --username="$DST_USER" --dbname="postgres" \
    --command="SELECT 1" --tuples-only \
    --quiet 2>/dev/null | grep -q 1 && true   # connectivity check

psql \
    --host="$DST_HOST" --port="$DST_PORT" \
    --username="$DST_USER" --dbname="postgres" \
    --command="CREATE DATABASE $DST_DB;" 2>/dev/null || \
    echo "  Database '$DST_DB' already exists — skipping."

# ---------- 2. Apply schema (enums, tables, indexes, triggers) ---------------
echo "[2/4] Applying schema from 01_schema_postgresql.sql..."
psql \
    --host="$DST_HOST" --port="$DST_PORT" \
    --username="$DST_USER" --dbname="$DST_DB" \
    --file="$OBRA_SCHEMA"

# ---------- 3. Restore data --------------------------------------------------
echo "[3/4] Restoring data..."

if [[ -f "$FULL_DUMP" ]]; then
    echo "  Using custom-format dump (pg_restore)..."
    pg_restore \
        --host="$DST_HOST" --port="$DST_PORT" \
        --username="$DST_USER" --dbname="$DST_DB" \
        --data-only --no-owner --no-acl \
        --disable-triggers \
        "$FULL_DUMP" || true   # non-fatal: data may already exist after schema seeding
elif [[ -f "$DATA_SQL" ]]; then
    echo "  Using plain-SQL INSERT dump (fallback)..."
    psql \
        --host="$DST_HOST" --port="$DST_PORT" \
        --username="$DST_USER" --dbname="$DST_DB" \
        --file="$DATA_SQL"
else
    echo "  WARNING: No data file found — schema is set up but no data imported."
fi

# ---------- 4. Verify row counts ---------------------------------------------
echo "[4/4] Verifying row counts..."
psql \
    --host="$DST_HOST" --port="$DST_PORT" \
    --username="$DST_USER" --dbname="$DST_DB" \
    --command="
SELECT 'users'               AS \"table\", COUNT(*) FROM users
UNION ALL
SELECT 'projects',                         COUNT(*) FROM projects
UNION ALL
SELECT 'project_users',                    COUNT(*) FROM project_users
UNION ALL
SELECT 'accessories',                      COUNT(*) FROM accessories
UNION ALL
SELECT 'external_inspections',             COUNT(*) FROM external_inspections
UNION ALL
SELECT 'site_inspections',                 COUNT(*) FROM site_inspections
UNION ALL
SELECT 'decommission_records',             COUNT(*) FROM decommission_records
UNION ALL
SELECT 'audit_logs',                       COUNT(*) FROM audit_logs
ORDER BY 1;
"

echo ""
echo "=== Import complete ==="
echo ""
echo "Next steps:"
echo "  1. Update the backend DATABASE_URL in your homelab .env:"
echo "     DATABASE_URL=postgresql+asyncpg://$DST_USER:\$PASSWORD@$DST_HOST:$DST_PORT/$DST_DB"
echo "  2. Transfer the media/uploads folder (photo files) to the homelab."
echo "  3. Update UPLOADS_DIR in .env to match the new path."
echo "  4. Change the default admin password at /api/v1/auth/change-password."
