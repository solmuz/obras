# OBRAS — Migration Guide (dev → homelab)

## Files in this folder

| File | Purpose |
|------|---------|
| `01_schema_postgresql.sql` | Creates all ENUM types, tables, indexes and triggers on the destination PostgreSQL server |
| `02_export_data.ps1` | Runs on the **Windows dev machine** — dumps data using `pg_dump` |
| `03_import_homelab.sh` | Runs on the **homelab server** (Linux/Docker) — creates the DB, applies schema, restores data |
| `04_verify_migration.sql` | Integrity check: row counts, FK orphan check, admin user confirmation |

---

## Pre-requisites

### Dev machine (Windows)
- PostgreSQL tools in PATH (`pg_dump`, `psql`). These ship with the PostgreSQL installer.
- PowerShell 5.1+

### Homelab server
- PostgreSQL 14+ running.
- `psql` and `pg_restore` in PATH.
- The `database/migration/` folder copied over (e.g. via SCP or a shared folder).

---

## Step-by-step

### 1 — Export from the dev machine

Open PowerShell in `database/migration/` and run:

```powershell
# Edit the password if needed (default: admin)
.\02_export_data.ps1
```

This creates `export_YYYYMMDD_HHmmss/` containing:
- `full_dump.pgdump` — binary dump (fastest restore)
- `data_inserts.sql` — plain-SQL fallback
- `schema_only.sql` — reference schema from the source DB

### 2 — Transfer files to the homelab

Copy the entire `database/migration/` folder to your homelab server:

```bash
# from the Windows machine (WSL / Git Bash / SCP client)
scp -r database/migration user@homelab-ip:/opt/obras/migration
```

Or use any other file transfer method (SMB share, USB, rsync).

### 3 — Apply schema + restore data on the homelab

```bash
cd /opt/obras/migration

# Set destination credentials (override defaults)
export PGPASSWORD="your_postgres_password"
export PGUSER="postgres"
export PGHOST="localhost"        # or the Docker container hostname
export PGPORT="5432"
export PGDATABASE="obras_db"

bash 03_import_homelab.sh export_YYYYMMDD_HHmmss
```

> If running PostgreSQL inside Docker:
> ```bash
> export PGHOST="127.0.0.1"
> # and make sure port 5432 is published: -p 5432:5432
> ```

### 4 — Verify

```bash
psql -U postgres -d obras_db -f 04_verify_migration.sql
```

All FK integrity checks should show **0 orphans**.

### 5 — Update backend `.env` on the homelab

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/obras_db
JWT_SECRET=<new strong secret — generate with: openssl rand -hex 32>
UPLOADS_DIR=/opt/obras/uploads
```

### 6 — Transfer uploaded photos/files

```bash
scp -r C:/Users/Josmuz/OBRAS/backend/uploads user@homelab-ip:/opt/obras/uploads
```

### 7 — Start the backend

```bash
cd /opt/obras/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Notes

- The schema script is **idempotent** (`IF NOT EXISTS` / `ON CONFLICT DO NOTHING`). Running it twice is safe.
- The default admin account seeded by the schema is `admin@obras.local` / `Admin1234!` — change the password immediately after first login.
- `photo_urls` columns use PostgreSQL native arrays (`VARCHAR(500)[]`) — not JSON — matching the `ARRAY(String)` SQLAlchemy type.
- Audit logs use `JSONB` (not `JSON`) for better indexing performance on the homelab.
