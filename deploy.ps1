# Cloud Run Deployment Script for Classroom Announcement App (PowerShell)
# This script builds and deploys the application to Google Cloud Run

# Configuration
$PROJECT_ID = "your-project-id"  # Replace with your Google Cloud Project ID
$SERVICE_NAME = "classroom-announcement-app"
$REGION = "us-central1"  # Change to your preferred region
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "🚀 Starting deployment to Google Cloud Run..." -ForegroundColor Green

# Check if gcloud is installed
if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Google Cloud SDK is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is installed
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Visit: https://docs.docker.com/get-docker/" -ForegroundColor Yellow
    exit 1
}

# Set the project
Write-Host "📋 Setting Google Cloud project to: $PROJECT_ID" -ForegroundColor Blue
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "🔧 Enabling required Google Cloud APIs..." -ForegroundColor Blue
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the Docker image
Write-Host "🐳 Building Docker image..." -ForegroundColor Blue
docker build -t $IMAGE_NAME .

# Push the image to Google Container Registry
Write-Host "📤 Pushing image to Google Container Registry..." -ForegroundColor Blue
docker push $IMAGE_NAME

# Deploy to Cloud Run
Write-Host "☁️ Deploying to Cloud Run..." -ForegroundColor Blue
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --port 8080 `
    --memory 512Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 10 `
    --set-env-vars DJANGO_SETTINGS_MODULE=classroom_announcement.settings_production

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your application is available at:" -ForegroundColor Green
gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"
