# Life OS - Database Persistence Guide

## Current Issue
Tasks and transactions added on mobile/Render are lost after service restart because Render's free tier has **ephemeral storage** (resets every ~15 minutes of inactivity).

## Solutions

### Option 1: Use Render PostgreSQL (Recommended) ⭐
1. Go to Render Dashboard
2. Create a new "PostgreSQL" database
3. Get the connection string
4. Update `.env` with: `DATABASE_URL=<your_postgres_url>`
5. We'll update database.py to use PostgreSQL

### Option 2: Upgrade Render Plan
- Render Starter ($7/month) includes persistent storage
- Data survives service restarts

### Option 3: Current Workaround
- Data persists during your active session
- Gets cleared on service inactivity/restart
- Perfect for testing, not ideal for production

## To Enable Persistent Storage on Render:

1. **For your service**, scroll to "Disks"
2. Click "Add Disk"
3. Set mount path: `/data`
4. Size: 1GB (free tier)
5. Redeploy service

This will preserve the `life_os.db` file even after restarts!

## Recommended: Use PostgreSQL

PostgreSQL is better because:
✅ Permanent data storage
✅ Can be accessed from multiple devices
✅ No file system limitations
✅ Scalable for future growth

Let us know if you'd like to set it up!
