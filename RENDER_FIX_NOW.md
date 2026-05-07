# 🚀 RENDER DEPLOYMENT FIX - STEP BY STEP

## ⚠️ The Problem

Render was deploying an **older version** of your code that tried to load the model eagerly at startup. The latest commit (863f8df) has been pushed with lazy loading fixes.

## ✅ What's Been Fixed

1. **Lazy Model Loading** - Model loads on first request, NOT at startup
2. **Correct Path Resolution** - Uses `__file__` instead of `os.getcwd()`
3. **Better Error Messages** - Shows detailed path info on failures
4. **tflite Model** - Uses correct `model.tflite` instead of `model.h5`

## 🔧 IMMEDIATE STEPS TO DEPLOY

### Step 1: Go to Render Dashboard
- Navigate to https://dashboard.render.com
- Click on your **food-freshness-api** service

### Step 2: Redeploy Latest Code
**Option A: Manual Redeploy (Recommended)**
1. In Render Dashboard, click your service name
2. Scroll down to find the **Deploy** section
3. Click **"Manual Deploy"** button
4. Select **"Deploy latest commit"**
5. Wait 2-3 minutes for build and deploy to complete

**Option B: Force Clear Redeploy**
1. Click **Settings** (gear icon)
2. Scroll down to **Danger Zone**
3. Click **Clear Build Cache**
4. Click **Manual Deploy** → **Deploy latest commit**

### Step 3: Monitor the Build
1. Click on your service
2. Go to the **Logs** tab
3. Wait for:
   ```
   ==> Build successful 🎉
   ==> Deploying...
   2026-05-07 XX:XX:XX: I tensorflow/core/platform/cpu_feature_guard.cc:182]
   ✅ Flask app initializing...
   ```
4. When you see `gunicorn` output without errors, the deploy worked!

### Step 4: Test the Deployment

```bash
# Get your service URL from Render Dashboard (looks like: https://xxxx.onrender.com)

# Test 1: Health endpoint (shows model loaded status)
curl https://YOUR_SERVICE_URL/api/health

# Should return:
{
  "status": "OK",
  "model_loaded": true,
  "model_path": "/opt/render/project/artifacts/model.tflite"
}

# Test 2: Make a prediction (with a test image)
curl -X POST https://YOUR_SERVICE_URL/api/predict \
  -F "image=@test_image.jpg"
```

## 📋 What Changed in the Code

### app.py
- **Before**: `predictor = PredictPipeline(MODEL_PATH)` ❌ (crashes if model not found)
- **After**: `predictor = None` + lazy loading function ✅ (loads on first request)

### Lazy Loading Function
```python
def get_predictor():
    """Lazy load predictor on first use"""
    global predictor
    if predictor is None:
        print("📦 Loading model predictor...")
        predictor = PredictPipeline(MODEL_PATH)
    return predictor
```

## ❌ If Deploy Still Fails

### Check Render Logs for Details
1. Dashboard → Your Service → **Logs** tab
2. Look for the error message
3. Common fixes:

#### Issue: `Model not found`
- Check model files exist: `git ls-files artifacts/`
- If missing: `git add artifacts/model.tflite && git push`

#### Issue: `Module not found: src.Pipeline`
- Your project structure has `/src/` folder
- This is correct - Render should handle it
- If error persists, check `.gitignore` - make sure `src/` is NOT ignored

#### Issue: `gunicorn: command not found`
- Ensure `gunicorn==21.2.0` is in requirements.txt ✓
- Already verified it's there

#### Issue: `tensorflow` errors
- These are normal at startup (GPU warnings, TF-TRT warnings)
- Ignore if app starts successfully after

### Clear Everything and Redeploy
```bash
# Option 1: In Render Dashboard
Settings → Danger Zone → Clear Build Cache → Manual Deploy

# Option 2: Push new commit to force redeploy
git commit --allow-empty -m "Force Render redeploy"
git push origin main
```

## 🧪 Test Locally First (Recommended)

Before relying on Render, test locally:

```bash
# 1. Ensure your conda/venv is active
# 2. Install deps
pip install -r requirements.txt

# 3. Run app
python app.py

# 4. In another terminal, test
curl http://localhost:10000/api/health
curl -X POST http://localhost:10000/api/predict -F "image=@test.jpg"
```

## 📊 Render Service Configuration

Your render.yaml specifies:
- **Python**: 3.11.9 ✓
- **Build**: `pip install -r requirements.txt` ✓
- **Start**: `gunicorn app:app --bind 0.0.0.0:$PORT` ✓
- **Environment**: Free tier ✓

## 🔍 Git Commits

Latest commits that fixed the issue:
```
863f8df - Force redeploy with lazy loading model ← LATEST
45936d1 - Add Render quick start deployment guide
7d1c412 - Fix Render deployment: lazy load model, improve path resolution
```

All are pushed to GitHub main branch and ready for Render to deploy.

## ⏱️ Timeline

1. **Now**: Run Manual Deploy on Render Dashboard
2. **2-3 min**: Build and deployment
3. **3-4 min**: Test `/api/health` endpoint
4. **4-5 min**: Test prediction with image

## 📞 Still Having Issues?

1. **Check Logs**: Render Dashboard → Logs tab
2. **Check Commit**: Render shows which commit it deployed (should be 863f8df)
3. **Force Redeploy**: Clear cache + manual deploy
4. **Verify Git**: `git log --oneline -1` shows latest commit pushed

## ✨ Expected Success Output

```
==> Build successful 🎉
==> Deploying...
==> Setting WEB_CONCURRENCY=1
✅ Flask app initializing...
🔥 BASE_DIR: /opt/render/project/src
🔥 MODEL_PATH: /opt/render/project/src/artifacts/model.tflite
🔥 Model exists: True
✅ App will load model on first request (lazy loading)
```

Then when you call `/api/predict`:
```
📦 Loading model predictor...
✅ TFLite model loaded successfully
```

---

**Status**: ✅ All fixes committed and pushed to GitHub
**Next Step**: Redeploy on Render Dashboard
**Expected Result**: Working API with model predictions
