# Azure Deployment Guide - Smart Assist

Complete guide for deploying the Smart Assist application to Microsoft Azure.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Azure Services Setup](#azure-services-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Database Configuration](#database-configuration)
7. [Azure AI Foundry Integration](#azure-ai-foundry-integration)
8. [Environment Variables](#environment-variables)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Debugging Guide](#debugging-guide)
11. [Troubleshooting](#troubleshooting)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Azure Cloud                              │
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │  Static Web App  │         │   App Service    │              │
│  │   (Frontend)     │────────>│    (Backend)     │              │
│  │  React + Vite    │         │     FastAPI      │              │
│  └──────────────────┘         └────────┬─────────┘              │
│                                         │                         │
│                                         ├─────────────────┐      │
│                                         │                 │      │
│                              ┌──────────▼──────┐  ┌──────▼────┐ │
│                              │  Azure SQL DB   │  │  AI       │ │
│                              │  (Financial     │  │  Foundry  │ │
│                              │   Data)         │  │  (Claude) │ │
│                              └─────────────────┘  └───────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               Application Insights (Monitoring)             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Tools

- **Azure CLI**: [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Azure Account**: Active subscription with appropriate permissions
- **Git**: For source control and deployment
- **Node.js 18+**: For frontend build
- **Python 3.11+**: For backend

### Azure Subscription Requirements

- Contributor or Owner role on subscription
- Ability to create:
  - App Services
  - Static Web Apps
  - Azure SQL Database
  - Azure AI Foundry resources
  - Application Insights

### Install Azure CLI

```bash
# macOS
brew install azure-cli

# Windows
# Download from: https://aka.ms/installazurecliwindows

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installation
az --version
```

### Login to Azure

```bash
az login

# Set your subscription (if you have multiple)
az account list --output table
az account set --subscription "Your-Subscription-Name"
```

## Azure Services Setup

### 1. Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="smart-assist-rg"
LOCATION="eastus"  # or your preferred region

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 2. Create Azure SQL Database

```bash
# Set variables
SQL_SERVER_NAME="smart-assist-sql-server"
SQL_DB_NAME="financial_insights_db"
SQL_ADMIN_USER="sqladmin"
SQL_ADMIN_PASSWORD="YourSecurePassword123!"  # Use a strong password

# Create SQL Server
az sql server create \
  --name $SQL_SERVER_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $SQL_ADMIN_USER \
  --admin-password $SQL_ADMIN_PASSWORD

# Configure firewall to allow Azure services
az sql server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER_NAME \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Create database
az sql db create \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER_NAME \
  --name $SQL_DB_NAME \
  --service-objective S0 \
  --backup-storage-redundancy Local

# Get connection string
az sql db show-connection-string \
  --client ado.net \
  --server $SQL_SERVER_NAME \
  --name $SQL_DB_NAME
```

### 3. Create Azure AI Foundry Resource

```bash
# Create AI Foundry workspace (requires Azure AI Foundry enabled)
AI_PROJECT_NAME="smart-assist-ai"

# Use Azure Portal to create AI Foundry project:
# 1. Go to https://ai.azure.com
# 2. Create new project: smart-assist-ai
# 3. Deploy Claude 3.5 Sonnet model
# 4. Note down connection string and endpoint
```

### 4. Create Application Insights

```bash
APP_INSIGHTS_NAME="smart-assist-insights"

# Create Application Insights
az monitor app-insights component create \
  --app $APP_INSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Get instrumentation key
az monitor app-insights component show \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv
```

## Backend Deployment

### Option 1: Azure App Service (Recommended)

```bash
APP_SERVICE_PLAN="smart-assist-plan"
BACKEND_APP_NAME="smart-assist-backend"

# Create App Service Plan (Linux)
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --runtime "PYTHON:3.11"

# Configure deployment from Git
cd backend
git init
git remote add azure https://<deployment-username>@$BACKEND_APP_NAME.scm.azurewebsites.net/$BACKEND_APP_NAME.git

# Set environment variables (see Environment Variables section)
az webapp config appsettings set \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    API_HOST="0.0.0.0" \
    API_PORT="8000" \
    MSSQL_SERVER="$SQL_SERVER_NAME.database.windows.net" \
    MSSQL_DATABASE="$SQL_DB_NAME" \
    MSSQL_USERNAME="$SQL_ADMIN_USER" \
    MSSQL_PASSWORD="$SQL_ADMIN_PASSWORD"

# Enable logging
az webapp log config \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --application-logging filesystem \
  --level information

# Deploy
git add .
git commit -m "Initial backend deployment"
git push azure main
```

### Option 2: Azure Container Instances

```bash
# Build and push Docker image
CONTAINER_REGISTRY_NAME="smartassistacr"

# Create container registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_REGISTRY_NAME \
  --sku Basic

# Login to registry
az acr login --name $CONTAINER_REGISTRY_NAME

# Build and push
cd backend
docker build -t $CONTAINER_REGISTRY_NAME.azurecr.io/backend:latest .
docker push $CONTAINER_REGISTRY_NAME.azurecr.io/backend:latest

# Deploy to Container Instance
az container create \
  --resource-group $RESOURCE_GROUP \
  --name smart-assist-backend \
  --image $CONTAINER_REGISTRY_NAME.azurecr.io/backend:latest \
  --cpu 1 \
  --memory 1.5 \
  --registry-login-server $CONTAINER_REGISTRY_NAME.azurecr.io \
  --registry-username $(az acr credential show --name $CONTAINER_REGISTRY_NAME --query username -o tsv) \
  --registry-password $(az acr credential show --name $CONTAINER_REGISTRY_NAME --query passwords[0].value -o tsv) \
  --dns-name-label smart-assist-backend \
  --ports 8000 \
  --environment-variables \
    API_HOST=0.0.0.0 \
    API_PORT=8000
```

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Frontend Deployment

### Azure Static Web Apps

```bash
FRONTEND_APP_NAME="smart-assist-frontend"

# Build frontend
cd frontend
npm install
npm run build

# Create Static Web App
az staticwebapp create \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Get deployment token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.apiKey \
  --output tsv)

# Deploy using Azure Static Web Apps CLI
npm install -g @azure/static-web-apps-cli
swa deploy ./dist \
  --deployment-token $DEPLOYMENT_TOKEN \
  --app-name $FRONTEND_APP_NAME

# Configure API backend URL
az staticwebapp appsettings set \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --setting-names VITE_API_URL="https://$BACKEND_APP_NAME.azurewebsites.net"
```

### Alternative: Azure Storage Static Website

```bash
STORAGE_ACCOUNT_NAME="smartassiststorage"

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Enable static website hosting
az storage blob service-properties update \
  --account-name $STORAGE_ACCOUNT_NAME \
  --static-website \
  --index-document index.html \
  --404-document index.html

# Upload files
cd frontend/dist
az storage blob upload-batch \
  --account-name $STORAGE_ACCOUNT_NAME \
  --source . \
  --destination '$web'

# Get website URL
az storage account show \
  --name $STORAGE_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query primaryEndpoints.web \
  --output tsv
```

## Database Configuration

### Initialize Database Schema

```bash
# Connect to Azure SQL
sqlcmd -S $SQL_SERVER_NAME.database.windows.net -d $SQL_DB_NAME -U $SQL_ADMIN_USER -P $SQL_ADMIN_PASSWORD

# Or use Azure Data Studio / SQL Server Management Studio

# Run schema creation scripts
sqlcmd -S $SQL_SERVER_NAME.database.windows.net \
  -d $SQL_DB_NAME \
  -U $SQL_ADMIN_USER \
  -P $SQL_ADMIN_PASSWORD \
  -i ../financial-insights-agents/database/sample_schema/create_tables.sql

# Load sample data
sqlcmd -S $SQL_SERVER_NAME.database.windows.net \
  -d $SQL_DB_NAME \
  -U $SQL_ADMIN_USER \
  -P $SQL_ADMIN_PASSWORD \
  -i ../financial-insights-agents/database/sample_schema/seed_data.sql
```

### Connection String Format

```
Server=tcp:{server_name}.database.windows.net,1433;
Database={database_name};
User ID={username};
Password={password};
Encrypt=yes;
TrustServerCertificate=no;
Connection Timeout=30;
```

## Azure AI Foundry Integration

### Setup Claude Model

1. **Create AI Foundry Project**:
   - Go to [Azure AI Foundry](https://ai.azure.com)
   - Create new project
   - Select region

2. **Deploy Claude Model**:
   ```bash
   # Using Azure CLI (if available)
   az ml online-deployment create \
     --name claude-deployment \
     --model claude-3-5-sonnet \
     --resource-group $RESOURCE_GROUP
   ```

3. **Get Credentials**:
   - Navigate to project settings
   - Copy connection string
   - Copy API endpoint
   - Copy deployment name

4. **Configure Backend**:
   - Add to environment variables
   - Test connection

## Environment Variables

### Backend Environment Variables

Create in Azure App Service Configuration:

```bash
# Required
AZURE_AI_PROJECT_CONNECTION_STRING="<your-connection-string>"
AZURE_OPENAI_ENDPOINT="<your-endpoint>"
AZURE_OPENAI_API_KEY="<your-api-key>"
AZURE_OPENAI_DEPLOYMENT_NAME="claude-3-5-sonnet"
MSSQL_SERVER="<server>.database.windows.net"
MSSQL_DATABASE="financial_insights_db"
MSSQL_USERNAME="<username>"
MSSQL_PASSWORD="<password>"

# Optional
API_HOST="0.0.0.0"
API_PORT="8000"
ENVIRONMENT="production"
DEBUG="false"
LOG_LEVEL="INFO"
APPLICATIONINSIGHTS_CONNECTION_STRING="<insights-connection-string>"
```

### Frontend Environment Variables

Configure in Static Web App or build process:

```bash
VITE_API_URL="https://smart-assist-backend.azurewebsites.net"
```

## Monitoring and Logging

### Application Insights Setup

```bash
# Enable Application Insights for backend
az webapp config appsettings set \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    APPLICATIONINSIGHTS_CONNECTION_STRING="<connection-string>"

# View logs
az monitor app-insights metrics show \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --metric requests/count

# Stream live logs
az webapp log tail \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### Log Analytics Queries

```kusto
// Request failures
requests
| where success == false
| project timestamp, name, resultCode, duration
| order by timestamp desc

// Slow requests
requests
| where duration > 5000
| project timestamp, name, duration
| order by duration desc

// Exception tracking
exceptions
| project timestamp, type, outerMessage, innermostMessage
| order by timestamp desc
```

## Debugging Guide

### Backend Debugging

#### 1. Enable Debug Mode

```bash
az webapp config appsettings set \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings DEBUG="true"
```

#### 2. View Application Logs

```bash
# Stream logs
az webapp log tail \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP

# Download logs
az webapp log download \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --log-file logs.zip
```

#### 3. SSH into Container

```bash
# Enable SSH
az webapp create-remote-connection \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP

# Or use portal: https://portal.azure.com
# Navigate to: App Service > Development Tools > SSH
```

#### 4. Test API Endpoints

```bash
# Health check
curl https://$BACKEND_APP_NAME.azurewebsites.net/health

# Test chat endpoint
curl -X POST https://$BACKEND_APP_NAME.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Frontend Debugging

#### 1. Check Build Output

```bash
cd frontend
npm run build
# Check dist/ folder
```

#### 2. Test Locally Against Azure Backend

```bash
# Update .env
echo "VITE_API_URL=https://$BACKEND_APP_NAME.azurewebsites.net" > .env

# Run locally
npm run dev
```

#### 3. Browser Console

- Open DevTools (F12)
- Check Console for errors
- Check Network tab for API calls
- Verify CORS headers

### Database Debugging

#### 1. Test Connection

```bash
sqlcmd -S $SQL_SERVER_NAME.database.windows.net \
  -d $SQL_DB_NAME \
  -U $SQL_ADMIN_USER \
  -P $SQL_ADMIN_PASSWORD \
  -Q "SELECT @@VERSION"
```

#### 2. Query Data

```sql
-- Check tables
SELECT * FROM INFORMATION_SCHEMA.TABLES;

-- Test data
SELECT TOP 10 * FROM portfolios;
SELECT TOP 10 * FROM holdings;
```

#### 3. Check Firewall Rules

```bash
az sql server firewall-rule list \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER_NAME \
  --output table
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Backend Not Starting

**Problem**: App Service shows "Service Unavailable"

**Solutions**:
```bash
# Check logs
az webapp log tail --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP

# Verify Python runtime
az webapp config show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP

# Restart app
az webapp restart --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP
```

#### 2. Database Connection Fails

**Problem**: "Cannot connect to database"

**Solutions**:
```bash
# Check firewall rules
az sql server firewall-rule list --server $SQL_SERVER_NAME --resource-group $RESOURCE_GROUP

# Add your IP
MY_IP=$(curl -s ifconfig.me)
az sql server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER_NAME \
  --name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP

# Test connection
sqlcmd -S $SQL_SERVER_NAME.database.windows.net -d $SQL_DB_NAME -U $SQL_ADMIN_USER -P $SQL_ADMIN_PASSWORD -Q "SELECT 1"
```

#### 3. CORS Errors

**Problem**: Frontend can't call backend API

**Solutions**:
```bash
# Update CORS in backend code (main.py)
# Add frontend URL to allow_origins list

# Or configure in App Service
az webapp cors add \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "https://$FRONTEND_APP_NAME.azurestaticapps.net"
```

#### 4. AI Foundry Connection Issues

**Problem**: "Cannot connect to Claude model"

**Solutions**:
- Verify deployment name matches configuration
- Check API key is correct
- Ensure model is deployed and running
- Check quota limits in Azure AI Foundry

#### 5. Slow Performance

**Problem**: Application is slow

**Solutions**:
```bash
# Scale up App Service
az appservice plan update \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku P1V2

# Scale out (add instances)
az appservice plan update \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --number-of-workers 3

# Optimize database
az sql db update \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER_NAME \
  --name $SQL_DB_NAME \
  --service-objective S2
```

### Health Check Endpoints

Test these endpoints to verify deployment:

```bash
# Backend health
curl https://$BACKEND_APP_NAME.azurewebsites.net/health

# Backend API
curl https://$BACKEND_APP_NAME.azurewebsites.net/api/sessions

# Frontend
curl https://$FRONTEND_APP_NAME.azurestaticapps.net
```

## Cost Optimization

### Estimated Monthly Costs

- **App Service (B1)**: ~$13/month
- **Azure SQL (S0)**: ~$15/month
- **Static Web App**: Free tier available
- **Application Insights**: ~$2-10/month (based on usage)
- **Azure AI Foundry**: Pay-per-use (varies)

### Cost Reduction Tips

1. **Use Free Tiers**:
   - Static Web Apps (Free tier)
   - App Service (F1 free tier for testing)

2. **Auto-scale**:
   ```bash
   az monitor autoscale create \
     --resource-group $RESOURCE_GROUP \
     --resource $BACKEND_APP_NAME \
     --resource-type Microsoft.Web/serverfarms \
     --min-count 1 \
     --max-count 3 \
     --count 1
   ```

3. **Stop Non-Production Resources**:
   ```bash
   az webapp stop --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP
   ```

## Security Best Practices

1. **Use Managed Identity**: Avoid storing credentials
2. **Enable HTTPS Only**: Force HTTPS connections
3. **Key Vault**: Store secrets in Azure Key Vault
4. **Network Security**: Use VNet integration
5. **Regular Updates**: Keep dependencies updated

### Enable Managed Identity

```bash
# Enable system-assigned managed identity
az webapp identity assign \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP

# Grant access to SQL
# Use Azure Portal to add managed identity to SQL
```

## Backup and Disaster Recovery

### Database Backup

```bash
# Automated backups are enabled by default

# Create manual backup
az sql db export \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER_NAME \
  --name $SQL_DB_NAME \
  --storage-key-type StorageAccessKey \
  --storage-key <storage-key> \
  --storage-uri https://mystorageaccount.blob.core.windows.net/backups/backup.bacpac \
  --admin-user $SQL_ADMIN_USER \
  --admin-password $SQL_ADMIN_PASSWORD
```

### App Service Backup

```bash
# Configure backup
az webapp config backup create \
  --resource-group $RESOURCE_GROUP \
  --webapp-name $BACKEND_APP_NAME \
  --backup-name initial-backup \
  --container-url "https://mystorageaccount.blob.core.windows.net/backups?<sas-token>"
```

## Next Steps

1. Set up CI/CD with Azure DevOps or GitHub Actions
2. Configure custom domain and SSL
3. Implement authentication (Azure AD)
4. Set up monitoring alerts
5. Optimize performance
6. Regular security audits

## Support and Resources

- [Azure Documentation](https://docs.microsoft.com/azure)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [Azure AI Foundry](https://ai.azure.com)

---

**Last Updated**: December 2025
**Version**: 1.0.0
