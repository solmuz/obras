# =============================================================================
# OBRAS – Export data from the SOURCE server (Windows dev machine)
# Usage: Run from PowerShell in the database/migration folder.
#   .\02_export_data.ps1
#
# Requires: pg_dump in PATH (ships with PostgreSQL installation)
# =============================================================================

$ErrorActionPreference = "Stop"

# ---------- SOURCE connection ------------------------------------------------
$SRC_HOST   = "localhost"
$SRC_PORT   = "5432"
$SRC_DB     = "obras_db"
$SRC_USER   = "postgres"
# Set PGPASSWORD so pg_dump doesn't prompt
$env:PGPASSWORD = "admin"   # <-- change if your local password is different

# ---------- Output files -----------------------------------------------------
$TIMESTAMP  = Get-Date -Format "yyyyMMdd_HHmmss"
$OUT_DIR    = "$PSScriptRoot\export_$TIMESTAMP"
New-Item -ItemType Directory -Path $OUT_DIR -Force | Out-Null

Write-Host "=== OBRAS data export ===" -ForegroundColor Cyan
Write-Host "Source : $SRC_USER@$SRC_HOST:$SRC_PORT/$SRC_DB"
Write-Host "Output : $OUT_DIR"
Write-Host ""

# ---------- 1. Schema-only dump (for reference / diff) -----------------------
Write-Host "[1/3] Exporting schema..." -ForegroundColor Yellow
& pg_dump `
    --host=$SRC_HOST --port=$SRC_PORT `
    --username=$SRC_USER --dbname=$SRC_DB `
    --schema-only --no-owner --no-acl `
    --file="$OUT_DIR\schema_only.sql"

# ---------- 2. Data-only dump (plain SQL INSERTs — portable) -----------------
Write-Host "[2/3] Exporting data (INSERT format)..." -ForegroundColor Yellow
& pg_dump `
    --host=$SRC_HOST --port=$SRC_PORT `
    --username=$SRC_USER --dbname=$SRC_DB `
    --data-only --no-owner --no-acl `
    --column-inserts `
    --file="$OUT_DIR\data_inserts.sql"

# ---------- 3. Custom-format full dump (binary, for pg_restore) --------------
Write-Host "[3/3] Exporting full dump (custom format)..." -ForegroundColor Yellow
& pg_dump `
    --host=$SRC_HOST --port=$SRC_PORT `
    --username=$SRC_USER --dbname=$SRC_DB `
    --format=custom --no-owner --no-acl `
    --file="$OUT_DIR\full_dump.pgdump"

Write-Host ""
Write-Host "=== Export complete ===" -ForegroundColor Green
Write-Host "Files written to: $OUT_DIR"
Write-Host ""
Write-Host "Transfer these files to your homelab server:"
Write-Host "  full_dump.pgdump   -- fastest restore via pg_restore"
Write-Host "  data_inserts.sql   -- fallback: plain SQL if pg_restore is unavailable"
Write-Host "  schema_only.sql    -- schema reference only"
