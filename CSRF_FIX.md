# CSRF Login Fix for Production

## Changes Made

1. **Added Production CSRF and Session Cookie Settings** in `settings.py`:
   - `CSRF_COOKIE_SECURE = True` (only in production)
   - `SESSION_COOKIE_SECURE = True` (only in production)
   - `SESSION_COOKIE_SAMESITE = 'Lax'`
   - `CSRF_COOKIE_SAMESITE = 'Lax'`

## Important: Check Your Production Domain

Make sure your `CSRF_TRUSTED_ORIGINS` environment variable in Railway includes your **exact production domain**:

```bash
CSRF_TRUSTED_ORIGINS=https://your-actual-domain.com,https://www.your-actual-domain.com
```

If you're using Railway's default domain, it should be:
```bash
CSRF_TRUSTED_ORIGINS=https://danielwood-production.up.railway.app
```

## How to Verify

1. **Check your Railway environment variables:**
   - Go to your Railway project → Variables
   - Ensure `CSRF_TRUSTED_ORIGINS` includes your production URL with `https://`

2. **Check browser console for errors:**
   - Open DevTools (F12)
   - Look for CSRF errors in the Console tab
   - Check Network tab for failed requests

3. **Check if cookies are being set:**
   - In DevTools → Application → Cookies
   - You should see `csrftoken` and `sessionid` cookies
   - They should be marked as "Secure" in production

## Common Issues

### Issue 1: Domain Mismatch
If your production URL is different from `danielwood-production.up.railway.app`, update `CSRF_TRUSTED_ORIGINS`.

### Issue 2: HTTP vs HTTPS
Make sure you're using `https://` in `CSRF_TRUSTED_ORIGINS`, not `http://`.

### Issue 3: Missing Environment Variable
If `CSRF_TRUSTED_ORIGINS` isn't set in Railway, Django will use the default which might not include your domain.

## Quick Fix

Add this to your Railway environment variables:
```
CSRF_TRUSTED_ORIGINS=https://danielwood-production.up.railway.app
```

Or if you have a custom domain:
```
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Testing

After deploying, try logging in. If it still fails:
1. Check Railway logs for CSRF errors
2. Verify the domain in `CSRF_TRUSTED_ORIGINS` matches exactly
3. Ensure cookies are being set (check browser DevTools)

