# Supabase Migration Setup Guide

## ✅ Migration Complete!

All code changes are done. Here's what you need to do now:

---

## 📋 Your Next Steps

### 1. Install Dependencies
```bash
pip install psycopg2-binary
```

### 2. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign in / Create account
3. Click **"New Project"**
4. Fill in:
   - Organization: Create or select
   - Name: `paperstack-metrics`
   - Database Password: **SAVE THIS!**
   - Region: Choose closest (e.g., `us-west-1`)
   - Plan: Free tier
5. Wait 2 minutes for provisioning

### 3. Get Database Credentials
1. In Supabase Dashboard → **Project Settings** (gear icon)
2. Go to **Database** tab
3. Find **Connection Info** section
4. Copy these values:
   - Host (e.g., `db.xxxxxxxxxxxxx.supabase.co`)
   - Database name (usually `postgres`)
   - Port (usually `5432`)
   - User (usually `postgres`)
   - Password (the one you set)

### 4. Configure Environment
Copy `.env.example` to `.env` and fill in:
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_TYPE=postgres

SUPABASE_HOST=db.xxxxxxxxxxxxx.supabase.co
SUPABASE_PORT=5432
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your-password-here
```

### 5. Run Schema in Supabase
1. In Supabase Dashboard → **SQL Editor** (left sidebar)
2. Click **"New Query"**
3. Copy entire content from `backend/db/schema_postgres.sql`
4. Paste into editor
5. Click **"Run"**
6. Verify: Go to **Table Editor** → Should see `sessions`, `requests`, `chunks` tables

### 6. Test Connection
```bash
./start.sh
```

You should see:
```
📊 Initializing POSTGRES database...
✅ PostgreSQL connection successful. All tables exist.
```

---

## 🔄 Switching Between SQLite and PostgreSQL

Just change in `.env`:
```env
# Local development with SQLite
DATABASE_TYPE=sqlite

# Production with Supabase
DATABASE_TYPE=postgres
```

---

## 📁 What Changed

### New Files
- ✅ `backend/db/schema_postgres.sql` - PostgreSQL schema
- ✅ `.env.example` updated with Supabase config

### Modified Files
- ✅ `backend/db/connection.py` - Dual database support
- ✅ `backend/db/repository.py` - Dynamic SQL placeholders
- ✅ `backend/main.py` - Smart bootstrap for both DBs
- ✅ `requirements.txt` - Added `psycopg2-binary`

---

## 🎯 Key Technical Details

### Placeholder Conversion
- **SQLite**: Uses `?` → `VALUES (?, ?, ?)`
- **PostgreSQL**: Uses `%s` → `VALUES (%s, %s, %s)`
- Our code auto-converts via `_build_query()`

### Row Access
- Both return **dict-like rows** for compatibility
- SQLite: `sqlite3.Row`
- PostgreSQL: `RealDictCursor`

### Schema Differences
- `DATETIME` → `TIMESTAMP`
- `CURRENT_TIMESTAMP` → `NOW()`
- `AUTOINCREMENT` → `SERIAL`
- `INSERT OR IGNORE` → `INSERT ... ON CONFLICT DO NOTHING`

---

## 🐛 Troubleshooting

**"Failed to connect to PostgreSQL"**
- Check credentials in `.env`
- Verify Supabase project is active
- Check firewall/network

**"Missing tables"**
- Run `schema_postgres.sql` in Supabase SQL Editor
- Verify tables exist in Table Editor

**"Module 'psycopg2' not found"**
```bash
pip install psycopg2-binary
```

---

## ✅ Ready!
Once you've completed steps 1-6, your metrics will be stored in Supabase cloud instead of local SQLite!
