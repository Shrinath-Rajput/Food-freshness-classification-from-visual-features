# 🚀 Deployment Guide

## Local Development Deployment

### Prerequisites
- Python 3.8+
- Node.js 14+
- MySQL 5.7+

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup Node.js
cd Backend
npm install
```

### Step 2: Database Setup

```bash
# Using provided SQL file
mysql -u root -p < database_setup.sql

# Or manually
mysql -u root -p
> CREATE DATABASE food_db;
> USE food_db;
> [Run queries from database_setup.sql]
```

### Step 3: Configuration

**Flask (.env.flask):**
```env
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=8000
```

**Node.js (Backend/.env):**
```env
NODE_ENV=development
PORT=3000
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=food_db
```

### Step 4: Start Services

```bash
# Terminal 1: Flask API
python app.py

# Terminal 2: Node.js Backend
cd Backend
npm run dev
```

---

## Production Deployment

### Using Gunicorn + Nginx + PM2

#### 1. Production Configuration

**Flask (.env.flask):**
```env
FLASK_ENV=production
FLASK_DEBUG=False
```

**Node.js (Backend/.env):**
```env
NODE_ENV=production
PORT=3000
```

#### 2. Deploy Flask API with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Or create systemd service
sudo nano /etc/systemd/system/food-api.service
```

**food-api.service:**
```ini
[Unit]
Description=Food Freshness Classification API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 3. Deploy Node.js with PM2

```bash
# Install PM2 globally
npm install -g pm2

# Start with PM2
cd Backend
pm2 start index.js --name "food-backend"

# Save PM2 configuration
pm2 save

# Enable PM2 startup on boot
pm2 startup
```

#### 4. Configure Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/food-classification

upstream flask_api {
    server 127.0.0.1:8000;
}

upstream node_backend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Flask API
    location /api/ {
        proxy_pass http://flask_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Node.js Backend
    location / {
        proxy_pass http://node_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # SSL Configuration (Let's Encrypt)
    # listen 443 ssl http2;
    # ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
}
```

#### 5. Enable Nginx Configuration

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/food-classification /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Docker Deployment

### Dockerfile (Flask API)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Dockerfile (Node.js Backend)

```dockerfile
FROM node:14-slim

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY Backend/ .

EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: food_db
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database_setup.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"

  flask_api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    environment:
      FLASK_ENV: production
    volumes:
      - ./uploads:/app/uploads

  node_backend:
    build:
      context: .
      dockerfile: Backend/Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - flask_api
      - mysql
    environment:
      NODE_ENV: production
      FLASK_API_URL: http://flask_api:8000
      DB_HOST: mysql

volumes:
  mysql_data:
```

**Deploy with Docker Compose:**
```bash
docker-compose up -d
```

---

## Cloud Deployment

### AWS Deployment

1. **EC2 Instance Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip nodejs npm mysql-server nginx -y

# Clone repository
git clone https://github.com/your-repo.git
cd Food-Freshness-Classification
```

2. **RDS Database**
```bash
# Use AWS RDS MySQL
# Update DB connection in .env files
```

3. **S3 for Uploads** (Optional)
```python
# Use boto3 for S3 file storage
import boto3
s3 = boto3.client('s3')
```

### Heroku Deployment

1. **Create Procfile**
```
web: gunicorn app:app
worker: npm --prefix Backend start
```

2. **Deploy**
```bash
heroku login
heroku create food-freshness-app
git push heroku main
```

---

## Monitoring & Maintenance

### Application Monitoring

```bash
# View logs
pm2 logs

# Monitor resources
pm2 monit

# Restart services
pm2 restart all
pm2 stop all
pm2 delete all
```

### Database Maintenance

```sql
-- Backup
mysqldump -u root -p food_db > backup.sql

-- Optimize tables
OPTIMIZE TABLE results;

-- Check disk usage
SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size in MB"
FROM information_schema.tables
WHERE table_schema = 'food_db';
```

### Scheduled Tasks

```bash
# Daily backup with cron
0 2 * * * mysqldump -u root -p food_db > /backups/food_db_$(date +\%Y\%m\%d).sql

# Log rotation
logrotate -f /etc/logrotate.d/food-app
```

---

## Security Checklist

- [ ] Use HTTPS/SSL certificates
- [ ] Strong database password
- [ ] Firewall rules configured
- [ ] File upload validation
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Environment variables secured
- [ ] Regular backups scheduled
- [ ] Error logging without sensitive data
- [ ] Database user with limited permissions

---

## Performance Optimization

```bash
# Database connection pooling
# Cache predictions (Redis)
# CDN for static files
# Compress responses (gzip)
# Image optimization
# Database query optimization
```

---

## 🎯 Render.com Deployment (Recommended)

### Why Render?
- Free tier available
- Automatic Git deployment
- Built-in environment variables
- No credit card for free tier
- Easy scaling

### Prerequisites
1. GitHub account with your repo
2. Render.com account (free)
3. Model files committed to Git

### Important: Commit Model Files to Git

The most common issue is that model files aren't being deployed. You MUST commit them:

```bash
# Make sure artifacts folder is not in .gitignore
git add artifacts/model.tflite
git add artifacts/model.h5
git commit -m "Add trained models"
git push origin main
```

Verify in .gitignore:
- Remove any lines that exclude `artifacts/` or `*.h5` or `*.tflite`
- Keep other ignores like `dataset/`, `uploads/`, etc.

### Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Connect your GitHub repository

### Step 2: Deploy Flask API

1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Fill in the details:
   - **Name:** `food-freshness-api`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Click "Create Web Service"

### Step 3: Verify Deployment

```bash
# Health check endpoint
curl https://your-app.onrender.com/api/health

# Expected response:
{
  "status": "OK",
  "model_loaded": true,
  "model_path": "/opt/render/project/artifacts/model.tflite"
}

# Test prediction
curl -X POST https://your-app.onrender.com/api/predict \
  -F "image=@test_image.jpg"
```

### Step 4: Environment Variables (Optional)

In Render dashboard:
1. Go to Settings → Environment
2. Add variables if needed:
   - `PYTHONUNBUFFERED=true`

### Troubleshooting Render Deployment

**Issue: Model not found**

Solution: Ensure model files are committed:
```bash
git status  # Check if artifacts/ shows
git add artifacts/
git commit -m "Add model files"
git push origin main
```

**Issue: Build fails**

Check the Build Log in Render Dashboard:
- Click on your service
- Go to "Logs" tab
- Look for errors

**Issue: App crashes after deploy**

Check the Deploy Log:
1. Click your service
2. Go to "Logs" tab
3. Look at startup errors
4. Check `/api/health` endpoint for details

### render.yaml Configuration

Your project now includes `render.yaml` for auto-deployment:

```yaml
services:
  - type: web
    name: food-freshness-api
    runtime: python-3.11
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
    plan: free
```

### Monitoring & Logs

```bash
# View all logs
# In Render dashboard: Logs tab

# Stream logs in real-time (if SSH available):
ssh into container and run:
tail -f /var/log/service.log
```

### Database Integration (Optional)

If you want to use Render PostgreSQL:

1. Create PostgreSQL database in Render
2. Get connection string from Render dashboard
3. Update your app to use the connection string
4. Add environment variable:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/db
   ```

### Node.js Backend on Render (Optional)

To also deploy the Node.js backend:

1. Create another Web Service
2. Point to `Backend/` directory
3. Build Command: `npm install`
4. Start Command: `npm start`

### Domain & SSL

Render automatically provides:
- Free SSL certificate
- Subdomain: `your-app.onrender.com`

To use custom domain:
1. Settings → Custom Domain
2. Add your domain
3. Update DNS records per Render instructions

### Automatic Redeploys

Every time you push to `main` branch:
```bash
git push origin main  # Automatically triggers Render deploy
```

To manually trigger:
- Go to Render dashboard
- Click "Manual Deploy" → "Deploy latest commit"

---

## Final Deployment Checklist

- [ ] Models committed to Git (`git add artifacts/`)
- [ ] requirements.txt has all dependencies
- [ ] .gitignore doesn't exclude model files
- [ ] Environment variables configured
- [ ] API endpoints tested locally
- [ ] render.yaml created and configured
- [ ] Git changes pushed to main branch
- [ ] Render deploy completes successfully
- [ ] Health endpoint returns model_loaded: true
- [ ] Test prediction endpoint works
- [ ] Monitor logs for any runtime errors

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| High memory usage | Reduce worker count, optimize queries |
| Slow uploads | Increase nginx upload limit, optimize images |
| Database errors | Check connection, verify permissions |
| 502 Bad Gateway | Check upstream services |
| Timeout errors | Increase timeout values |

---

## Support & Documentation

- **Documentation**: See README.md
- **Quick Start**: See QUICK_START.md
- **API Docs**: http://yourdomain.com/api/
- **Issues**: Check logs in `logs/` directory

---

**Version**: 1.0.0  
**Last Updated**: April 2024
