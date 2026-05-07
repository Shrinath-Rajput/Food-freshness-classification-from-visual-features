# 🚀 FULL STACK DEPLOYMENT GUIDE - RENDER

## 📋 Overview

Your application has **TWO services**:
1. **Flask API** (Python) - `/api/predict`, `/api/health`
2. **Express Backend** (Node.js) - Web UI and database management

Both are now configured in `render.yaml` for Render deployment.

---

## 🎯 DEPLOYMENT STEPS

### Step 1: Set Up MySQL Database (Choose One Option)

#### Option A: Free MySQL Service (Recommended)
Use a free cloud database like:
- **PlanetScale** (MySQL compatible, free tier) - https://planetscale.com
- **Aiven** (MySQL free tier) - https://aiven.io
- **Clever Cloud** (MySQL free) - https://www.clever-cloud.com

Get your connection details:
```
MYSQL_HOST: xxxx.mysql.somewhere.com
MYSQL_USER: root
MYSQL_PASSWORD: your_password
MYSQL_DATABASE: food_db
MYSQL_PORT: 3306
```

#### Option B: Use Render's Database
1. Go to Render Dashboard
2. Click "New" → "MySQL Database"
3. Create database named `food_db`
4. Get connection details

### Step 2: Deploy Python Flask API

Status: ✅ **Already Deployed**

If you need to redeploy:
1. Go to https://dashboard.render.com
2. Click `food-freshness-api` service
3. Click "Manual Deploy" → "Deploy latest commit"

**Flask API URL**: (You'll see it in Render Dashboard)
```
https://food-freshness-api-xxxx.onrender.com
```

### Step 3: Create Node.js Backend Service

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Click "New Web Service"**

3. **Connect Repository**:
   - Repository: `Food-freshness-classification-from-visual-features`
   - Branch: `main`

4. **Configure Service**:

   | Field | Value |
   |-------|-------|
   | **Name** | `food-freshness-backend` |
   | **Runtime** | Node |
   | **Build Command** | `cd Backend && npm install --production` |
   | **Start Command** | `cd Backend && node index.js` |
   | **Plan** | Free |
   | **Region** | Oregon (or your preference) |

5. **Add Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `NODE_ENV` | `production` |
   | `FLASK_URL` | `https://food-freshness-api-xxxx.onrender.com` |
   | `MYSQL_HOST` | Your MySQL host |
   | `MYSQL_USER` | Your MySQL user |
   | `MYSQL_PASSWORD` | Your MySQL password |
   | `MYSQL_DATABASE` | `food_db` |
   | `MYSQL_PORT` | `3306` |

6. **Click "Create Web Service"**

---

## 🧪 Test Your Deployment

### Test Flask API
```bash
# Health check
curl https://food-freshness-api-xxxx.onrender.com/api/health

# Expected response:
{
  "status": "OK",
  "model_loaded": true,
  "model_path": "..."
}

# Test prediction
curl -X POST https://food-freshness-api-xxxx.onrender.com/api/predict \
  -F "image=@test_image.jpg"
```

### Test Express Backend
```bash
# Home page
curl https://food-freshness-backend-xxxx.onrender.com/

# Expected: HTML page loads

# Upload endpoint
curl -X POST https://food-freshness-backend-xxxx.onrender.com/upload \
  -F "file=@test_image.jpg" \
  -F "product_name=apple"
```

---

## 📊 Service Configuration Details

### Flask Python API Service

**Buildpack**: Python 3.11

**Build Command**:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Start Command**:
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 60
```

**Key Files**:
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `artifacts/model.tflite` - ML model

---

### Express Node.js Backend Service

**Buildpack**: Node.js

**Build Command**:
```bash
cd Backend && npm install --production
```

**Start Command**:
```bash
cd Backend && node index.js
```

**Key Files**:
- `Backend/index.js` - Main Express server
- `Backend/package.json` - Node dependencies
- `Backend/views/` - EJS templates
- `Backend/public/` - Static files (CSS, JS)

---

## 🔌 API Integration

The Express backend connects to Flask API:

```javascript
// Backend/index.js
const FLASK_URL = process.env.FLASK_URL;

// When user uploads image:
const formData = new FormData();
formData.append('image', imageFile);

axios.post(`${FLASK_URL}/api/predict`, formData)
  .then(response => {
    // Save result to database
    // Display to user
  });
```

**Update FLASK_URL environment variable with your Flask API URL!**

---

## 📱 Full Website Workflow

1. **User opens** `https://food-freshness-backend-xxxx.onrender.com/`
2. **Express backend** serves HTML form
3. **User uploads image** and fills product name
4. **Express backend** sends image to Flask API
5. **Flask API** runs ML model on image
6. **Flask API** returns prediction (class, confidence, freshness)
7. **Express backend** saves result to MySQL database
8. **Express backend** displays result to user

---

## 🆘 Troubleshooting

### Backend Service Won't Deploy

**Check logs**:
1. Dashboard → food-freshness-backend
2. Click "Logs" tab
3. Look for error messages

**Common Issues**:

| Error | Fix |
|-------|-----|
| `Cannot find module 'express'` | Ensure `npm install` runs successfully |
| `MYSQL_HOST not found` | Add environment variables in Render |
| `FLASK_URL connection refused` | Ensure Flask API is running and add correct URL |
| `Port already in use` | Delete old service and redeploy |

### MySQL Connection Issues

**Test connection**:
```bash
# From your local machine
mysql -h YOUR_MYSQL_HOST -u YOUR_USER -p
USE food_db;
SHOW TABLES;
```

If tables don't exist, the backend will create them automatically.

---

## 🚀 Your Two Services on Render

```
┌─────────────────────────────────────────────┐
│         Your Render Account                 │
├─────────────────────────────────────────────┤
│                                             │
│  ✅ food-freshness-api (Python)             │
│     URL: https://xxxx-api.onrender.com     │
│     /api/health → Health check             │
│     /api/predict → ML prediction           │
│                                             │
│  ✅ food-freshness-backend (Node.js)        │
│     URL: https://xxxx-backend.onrender.com │
│     / → Home page with upload form         │
│     /upload → Process and save result      │
│     /results → View past results           │
│                                             │
│  🗄️ MySQL Database                          │
│     Connected to Backend                   │
│     Stores results and history             │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📝 Environment Variables Summary

### Flask API (.env or Render Settings)
```
PYTHON_VERSION=3.11.9
PYTHONUNBUFFERED=true
```

### Node.js Backend (Render Settings)
```
NODE_ENV=production
FLASK_URL=https://food-freshness-api-xxxx.onrender.com
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=food_db
MYSQL_PORT=3306
```

---

## 🎯 Final URLs

Once deployed, you'll have:

**Frontend & Backend**:
```
https://food-freshness-backend-xxxx.onrender.com
```

**API Endpoints**:
```
https://food-freshness-api-xxxx.onrender.com/api/predict
https://food-freshness-api-xxxx.onrender.com/api/health
```

---

## ✨ Next Steps

1. ✅ Set up MySQL database (free service recommended)
2. ✅ Update render.yaml with your MySQL details
3. ✅ Create Node.js service on Render
4. ✅ Set environment variables
5. ✅ Deploy and test
6. ✅ Share your live URL!

---

**Status**: Ready to deploy to Render! 🚀
