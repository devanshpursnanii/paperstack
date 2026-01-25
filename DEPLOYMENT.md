# PaperStack Deployment Quick Reference

## Environment Variables for Backend

### Required for All Deployments
```bash
# Google API Keys
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_SEARCH_API_KEY=your_custom_search_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id

# Authentication
ACCESS_TOKEN=welcometopaperstack1

# Database Configuration
DATABASE_TYPE=postgres  # or "sqlite" for local

# PostgreSQL/Supabase (if DATABASE_TYPE=postgres)
SUPABASE_HOST=aws-1-ap-south-1.pooler.supabase.com
SUPABASE_PORT=6543
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres.niallidsslcpijjyxgah
SUPABASE_PASSWORD=your_supabase_password
```

### Optional
```bash
DATABASE_TYPE=sqlite  # Use SQLite instead of PostgreSQL (local dev only)
```

## Quick Deploy Checklist

### Backend (Railway/Render)
1. ✅ Create new service
2. ✅ Connect GitHub repo
3. ✅ Set root directory: `backend/`
4. ✅ Add all environment variables above
5. ✅ Set start command: `python main.py`
6. ✅ Deploy

### Frontend (Vercel)
1. ✅ Create new project
2. ✅ Connect GitHub repo
3. ✅ Set root directory: `frontend/`
4. ✅ Framework: Next.js
5. ✅ Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`
6. ✅ Deploy

## Changing Access Token (Post-Deploy)

### Railway
1. Dashboard → Your Service → Variables
2. Update `ACCESS_TOKEN` value
3. Auto-redeploys on save

### Render
1. Dashboard → Your Service → Environment
2. Update `ACCESS_TOKEN` value
3. Save → Manual Deploy

### Result
- All users logged out automatically
- Must enter new token to access app

## Database Setup (Supabase)

### Initial Setup
1. Create Supabase project
2. Go to Project Settings → Database
3. Copy connection pooler details (not direct connection!)
4. Run `backend/db/schema_postgres.sql` in SQL Editor
5. Set environment variables (pooler credentials)

### Connection Pooler (Recommended)
- **Host**: `aws-1-ap-south-1.pooler.supabase.com`
- **Port**: `6543`
- **User**: `postgres.<project_ref>`
- **Mode**: Session pooling
- Better for production deployments

## Local Development

### Start Backend
```bash
cd /Users/apple/Desktop/paperstack
/Users/apple/Desktop/paperstack/venv/bin/python backend/main.py
```
Runs on: http://localhost:8000

### Start Frontend
```bash
cd /Users/apple/Desktop/paperstack/frontend
npm run dev
```
Runs on: http://localhost:3000

## Testing Authentication

### Valid Token
```bash
curl -X POST http://localhost:8000/auth/validate \
  -H "Content-Type: application/json" \
  -d '{"token":"welcometopaperstack1"}'
```
Response: `{"valid":true,"message":"Token is valid"}`

### Protected Endpoint
```bash
curl -X POST http://localhost:8000/session/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer welcometopaperstack1" \
  -d '{"initial_query":"test"}'
```

## Security Recommendations

1. **Change Default Token**: Replace `welcometopaperstack1` with secure random token
2. **Generate Secure Token**:
   ```bash
   openssl rand -base64 32
   ```
3. **Rotate Regularly**: Update token every 2-3 months
4. **Never Commit**: Keep `.env` gitignored
5. **Use Different Tokens**: Dev vs Production vs Staging

## Monitoring

### Check Backend Logs
- **Railway**: Dashboard → Deployments → View Logs
- **Render**: Dashboard → Logs

### Check Failed Auth Attempts
Look for: `"Unauthorized access attempt"` in logs

## Troubleshooting

### 401 Errors on All Requests
- Verify `ACCESS_TOKEN` is set in deployment
- Check backend logs for startup errors
- Test `/auth/validate` endpoint directly

### Frontend Not Loading
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is accessible from frontend domain
- Check CORS settings in `backend/main.py`

### Database Connection Errors
- Use session pooler, not direct connection
- Verify Supabase credentials
- Check if database tables exist (run schema_postgres.sql)

## URLs Reference

### Local Development
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Backend Docs: http://localhost:8000/docs

### Production (Example)
- Frontend: https://paperstack.vercel.app
- Backend: https://paperstack-backend.railway.app
- Backend Docs: https://paperstack-backend.railway.app/docs
