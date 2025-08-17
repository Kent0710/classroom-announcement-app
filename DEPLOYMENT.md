# 🚀 Google Cloud Run Deployment Guide

This guide will help you deploy your Classroom Announcement Application to Google Cloud Run.

## 📋 Prerequisites

### 1. Google Cloud Setup
- **Google Cloud Account**: Create one at [cloud.google.com](https://cloud.google.com)
- **Google Cloud Project**: Create a new project or use existing one
- **Billing**: Enable billing for your project

### 2. Local Tools Installation

#### Install Google Cloud SDK
- **Windows**: Download from [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
- **macOS**: `brew install --cask google-cloud-sdk`
- **Linux**: Follow instructions on the Google Cloud SDK page

#### Install Docker
- **Windows**: Download Docker Desktop from [docker.com](https://docs.docker.com/get-docker/)
- **macOS**: Download Docker Desktop from [docker.com](https://docs.docker.com/get-docker/)
- **Linux**: Use your package manager (e.g., `sudo apt install docker.io`)

## 🛠️ Deployment Steps

### Step 1: Configure Google Cloud SDK

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Update Configuration

1. **Edit the deployment script**:
   - Open `deploy.ps1` (Windows) or `deploy.sh` (Linux/macOS)
   - Replace `your-project-id` with your actual Google Cloud project ID
   - Optionally change the region (default: us-central1)

2. **Generate a secure Django secret key**:
   ```python
   # Run this in a Python shell
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

### Step 3: Deploy to Cloud Run

#### For Windows (PowerShell):
```powershell
# Make sure you're in the project directory
cd "C:\Users\Christian Kent\Desktop\chls-software-innovations\classroom-announcement-app"

# Run the deployment script
.\deploy.ps1
```

#### For Linux/macOS (Bash):
```bash
# Make sure you're in the project directory
cd /path/to/classroom-announcement-app

# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

### Step 4: Manual Deployment (Alternative)

If the script doesn't work, you can deploy manually:

```bash
# Set variables
PROJECT_ID="your-project-id"
SERVICE_NAME="classroom-announcement-app"
REGION="us-central1"

# Build and push Docker image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --set-env-vars DJANGO_SETTINGS_MODULE=classroom_announcement.settings_production
```

## 🔧 Post-Deployment Configuration

### 1. Update ALLOWED_HOSTS

After deployment, update your production settings:

1. Get your Cloud Run URL from the deployment output
2. Edit `classroom_announcement/settings_production.py`
3. Add your Cloud Run URL to `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = [
    '.run.app',
    'your-service-url.run.app',  # Add your actual URL
    'localhost',
    '127.0.0.1',
]
```

### 2. Set Environment Variables

For production, set environment variables in Cloud Run:

```bash
gcloud run services update classroom-announcement-app \
    --region us-central1 \
    --set-env-vars SECRET_KEY="your-secure-secret-key"
```

### 3. Database Migration

Your app uses SQLite by default. For the first deployment:

```bash
# Connect to your Cloud Run instance and run migrations
gcloud run services proxy classroom-announcement-app --port=8080

# In another terminal, run migrations
curl -X POST https://your-service-url.run.app/admin/
```

## 🗄️ Database Options

### Option 1: SQLite (Current - Simple)
- Good for development and small applications
- Data persists in the container
- Limited scalability

### Option 2: Cloud SQL PostgreSQL (Recommended for Production)

1. Create a Cloud SQL instance:
```bash
gcloud sql instances create classroom-db \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro \
    --region=us-central1
```

2. Update `settings_production.py` to use PostgreSQL (uncomment the PostgreSQL section)

3. Set database environment variables in Cloud Run

## 🔒 Security Considerations

### 1. Generate Secure Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 2. Enable HTTPS (for custom domains)
```python
# In settings_production.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 3. Set Up Custom Domain (Optional)
```bash
gcloud run domain-mappings create \
    --service classroom-announcement-app \
    --domain your-domain.com \
    --region us-central1
```

## 📊 Monitoring and Logs

### View Logs
```bash
gcloud logs read --service=classroom-announcement-app
```

### Monitor Performance
- Visit [Google Cloud Console](https://console.cloud.google.com)
- Navigate to Cloud Run > classroom-announcement-app
- Check metrics and logs

## 💰 Cost Optimization

### Cloud Run Pricing
- **Free Tier**: 2 million requests per month
- **Pay per use**: Only charged when requests are being processed
- **Current configuration**: ~$5-20/month for moderate usage

### Optimization Tips
1. **Set min-instances to 0** (default) to avoid charges when idle
2. **Optimize memory allocation** (512Mi is sufficient for most use cases)
3. **Monitor usage** through Google Cloud Console

## 🚨 Troubleshooting

### Common Issues

1. **"Permission denied" errors**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Docker push fails**:
   ```bash
   gcloud auth configure-docker
   ```

3. **Service won't start**:
   - Check logs: `gcloud logs read --service=classroom-announcement-app`
   - Verify environment variables
   - Check ALLOWED_HOSTS setting

4. **Static files not loading**:
   - Ensure WhiteNoise is properly configured
   - Check static files collection in Dockerfile

### Getting Help

- **Google Cloud Support**: [cloud.google.com/support](https://cloud.google.com/support)
- **Cloud Run Documentation**: [cloud.google.com/run/docs](https://cloud.google.com/run/docs)
- **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com)

## 🎉 Success!

Once deployed successfully, your Classroom Announcement Application will be available at:
`https://your-service-name.run.app`

Share this URL with your users to access the application!
