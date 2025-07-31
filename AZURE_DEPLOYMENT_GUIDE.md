# Azure Container Apps Deployment Guide
## Novellus Loan Management System

This guide provides step-by-step instructions for deploying the Novellus Loan Management System to Azure Container Apps with PostgreSQL database.

## Prerequisites

1. **Azure Subscription** with appropriate permissions
2. **Azure CLI** installed and configured
3. **Docker** installed locally
4. **Git** for code management

## Step 1: Prepare Your Environment

### 1.1 Install Required Tools

```bash
# Install Azure CLI (if not already installed)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Docker (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install docker.io

# Login to Azure
az login
```

### 1.2 Set Environment Variables

```bash
# Set your Azure subscription
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="novellus-rg"
LOCATION="eastus"
ACR_NAME="novelluscr"
APP_NAME="novellus-loan-calculator"
DB_SERVER_NAME="novellus-db-server"
DB_NAME="novellus_loans"
CONTAINER_ENV="novellus-env"

# Set subscription
az account set --subscription $SUBSCRIPTION_ID
```

## Step 2: Create Azure Resources

### 2.1 Create Resource Group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 2.2 Create Azure Container Registry

```bash
# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR login server
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
echo "ACR Server: $ACR_SERVER"
```

### 2.3 Create PostgreSQL Database

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --location $LOCATION \
  --admin-user novellus_admin \
  --admin-password "NovellusSecure2025!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14 \
  --storage-size 32 \
  --high-availability Disabled \
  --zone 1

# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --database-name $DB_NAME

# Configure firewall to allow Azure services
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Get connection string
DB_HOST=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "fullyQualifiedDomainName" --output tsv)
DATABASE_URL="postgresql://novellus_admin:NovellusSecure2025!@$DB_HOST:5432/$DB_NAME"
echo "Database URL: $DATABASE_URL"
```

### 2.4 Create Container Apps Environment

```bash
# Install Container Apps extension
az extension add --name containerapp

# Register provider
az provider register --namespace Microsoft.App

# Create Container Apps environment
az containerapp env create \
  --name $CONTAINER_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

## Step 3: Build and Push Docker Image

### 3.1 Build Docker Image

```bash
# Navigate to your project directory
cd /path/to/novellus-loan-calculator

# Build Docker image
docker build -t $ACR_SERVER/novellus-loan-calculator:latest .

# Test image locally (optional)
docker run -p 5000:5000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e SESSION_SECRET="your-session-secret" \
  -e JWT_SECRET_KEY="your-jwt-secret" \
  $ACR_SERVER/novellus-loan-calculator:latest
```

### 3.2 Push to Azure Container Registry

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Push image
docker push $ACR_SERVER/novellus-loan-calculator:latest

# Verify image
az acr repository list --name $ACR_NAME --output table
```

## Step 4: Deploy Container App

### 4.1 Create Container App with Secrets

```bash
# Create secrets for database and keys
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_ENV \
  --image $ACR_SERVER/novellus-loan-calculator:latest \
  --registry-server $ACR_SERVER \
  --registry-username $ACR_NAME \
  --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv) \
  --secrets \
    database-url="$DATABASE_URL" \
    session-secret="NovellusSessionSecret2025!" \
    jwt-secret="NovellusJWTSecret2025!" \
  --env-vars \
    DATABASE_URL=secretref:database-url \
    SESSION_SECRET=secretref:session-secret \
    JWT_SECRET_KEY=secretref:jwt-secret \
    FLASK_ENV=production \
    FLASK_APP=main.py \
  --ingress external \
  --target-port 5000 \
  --cpu 1.0 \
  --memory 2Gi \
  --min-replicas 1 \
  --max-replicas 3
```

### 4.2 Get Application URL

```bash
# Get the application URL
APP_URL=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "configuration.ingress.fqdn" --output tsv)
echo "Application URL: https://$APP_URL"
```

## Step 5: Configure Custom Domain (Optional)

### 5.1 Add Custom Domain

```bash
# Add custom domain (replace with your domain)
CUSTOM_DOMAIN="loans.yourdomain.com"

az containerapp hostname add \
  --hostname $CUSTOM_DOMAIN \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# Bind SSL certificate (requires certificate upload)
az containerapp ssl upload \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --certificate-file /path/to/certificate.pfx \
  --certificate-password "your-cert-password"
```

## Step 6: Set Up Monitoring and Logging

### 6.1 Enable Application Insights

```bash
# Create Application Insights
az extension add --name application-insights

APPINSIGHTS_NAME="novellus-insights"

az monitor app-insights component create \
  --app $APPINSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --kind web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show --app $APPINSIGHTS_NAME --resource-group $RESOURCE_GROUP --query "instrumentationKey" --output tsv)

# Update container app with Application Insights
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

### 6.2 Configure Log Analytics

```bash
# Container Apps automatically use Log Analytics in the environment
# View logs:
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow
```

## Step 7: Configure Auto-Scaling

### 7.1 Set Up HTTP Scaling Rules

```bash
# Update scaling configuration
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 1 \
  --max-replicas 5 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-metadata concurrentRequests=50
```

## Step 8: Database Migration and Setup

### 8.1 Run Database Initialization

```bash
# Connect to the running container to initialize database
CONTAINER_ID=$(az containerapp replica list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[0].name" --output tsv)

# Execute database initialization (if needed)
az containerapp exec \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --replica $CONTAINER_ID \
  --command "python database_init.py"
```

## Step 9: Security Configuration

### 9.1 Network Security

```bash
# Restrict ingress to specific IPs (if needed)
az containerapp ingress update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --allow-insecure false

# Configure IP restrictions in Azure Portal if needed
```

### 9.2 Update Secrets

```bash
# Update secrets without redeployment
az containerapp secret set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --secrets session-secret="NewSessionSecret2025!"
```

## Step 10: Backup and Disaster Recovery

### 10.1 Database Backup

```bash
# Configure automated backups (default enabled)
az postgres flexible-server parameter set \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --name backup_retention_days \
  --value 7
```

### 10.2 Application Backup

```bash
# Export container app configuration
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  > containerapp-backup.json
```

## Step 11: CI/CD Setup (GitHub Actions)

### 11.1 Create Service Principal

```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "novellus-github-actions" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
```

### 11.2 GitHub Secrets

Add these secrets to your GitHub repository:

- `AZURE_CREDENTIALS`: Output from service principal creation
- `ACR_LOGIN_SERVER`: Your ACR server name
- `ACR_USERNAME`: ACR username
- `ACR_PASSWORD`: ACR password
- `RESOURCE_GROUP`: Your resource group name
- `CONTAINER_APP_NAME`: Your container app name

## Step 12: Monitoring and Maintenance

### 12.1 Health Checks

```bash
# Check application health
curl -f https://$APP_URL/

# View application metrics
az monitor metrics list \
  --resource /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$APP_NAME \
  --metric "Requests"
```

### 12.2 Update Application

```bash
# Build and push new version
docker build -t $ACR_SERVER/novellus-loan-calculator:v2 .
docker push $ACR_SERVER/novellus-loan-calculator:v2

# Update container app
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_SERVER/novellus-loan-calculator:v2
```

## Troubleshooting

### Common Issues

1. **Container fails to start**
   ```bash
   az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP
   ```

2. **Database connection issues**
   - Verify firewall rules
   - Check connection string
   - Ensure database is accessible from Azure

3. **Image pull failures**
   - Verify ACR credentials
   - Check image exists: `az acr repository show-tags --name $ACR_NAME --repository novellus-loan-calculator`

4. **SSL/Domain issues**
   - Verify DNS records point to Container App FQDN
   - Check certificate validity

### Useful Commands

```bash
# Scale manually
az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --min-replicas 2

# Restart application
az containerapp revision restart --name $APP_NAME --resource-group $RESOURCE_GROUP

# View environment variables
az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].env"

# Export logs
az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP > app-logs.txt
```

## Cost Optimization

1. **Use appropriate SKUs**
   - Start with Basic tier for ACR
   - Use Burstable tier for PostgreSQL in development

2. **Configure auto-scaling**
   - Set minimum replicas to 1
   - Scale based on actual usage patterns

3. **Monitor usage**
   - Use Azure Cost Management
   - Set up billing alerts

## Security Best Practices

1. **Secrets Management**
   - Use Container App secrets for sensitive data
   - Rotate secrets regularly
   - Consider Azure Key Vault for production

2. **Network Security**
   - Use private endpoints for database
   - Configure IP restrictions
   - Enable HTTPS only

3. **Database Security**
   - Use strong passwords
   - Enable SSL connections
   - Regular security updates

## Support and Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Azure PostgreSQL Documentation](https://docs.microsoft.com/azure/postgresql/)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)

---

**Note**: Replace all placeholder values with your actual Azure resources and credentials. Ensure you follow your organization's security policies for production deployments.