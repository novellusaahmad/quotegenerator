# Azure Container App Deployment Steps

This guide explains how to deploy the Quote Generator application to [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/).
## Prerequisites
- Azure subscription
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) logged in with `az login`
- [Docker](https://docs.docker.com/get-docker/) installed
- PostgreSQL admin password for the database

## 1. Create Azure Resources
```bash
# Variables
RESOURCE_GROUP="novellus-rg"
LOCATION="eastus"
ACR_NAME="novelluscr"
APP_NAME="novellus-loan-calculator"
DB_SERVER_NAME="novellus-db-server"
DB_NAME="novellus_loans"
CONTAINER_ENV="novellus-env"

# Resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Container registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)

# PostgreSQL flexible server and database
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --location $LOCATION \
  --admin-user novellus_admin \
  --admin-password "<DB_PASSWORD>" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 14

az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --database-name $DB_NAME

az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

DB_HOST=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "fullyQualifiedDomainName" --output tsv)
DATABASE_URL="postgresql://novellus_admin:<DB_PASSWORD>@$DB_HOST:5432/$DB_NAME"

# Container Apps environment
az extension add --name containerapp
az provider register --namespace Microsoft.App
az containerapp env create --name $CONTAINER_ENV --resource-group $RESOURCE_GROUP --location $LOCATION
```

## 2. Build and Push the Image
```bash
az acr login --name $ACR_NAME
docker build -t $ACR_SERVER/novellus-loan-calculator:latest .
docker push $ACR_SERVER/novellus-loan-calculator:latest
```

## 3. Deploy the Container App
```bash
SESSION_SECRET=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_ENV \
  --image $ACR_SERVER/novellus-loan-calculator:latest \
  --registry-server $ACR_SERVER \
  --registry-username $ACR_NAME \
  --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv) \
  --secrets database-url="$DATABASE_URL" session-secret="$SESSION_SECRET" jwt-secret="$JWT_SECRET" \
  --env-vars DATABASE_URL=secretref:database-url SESSION_SECRET=secretref:session-secret JWT_SECRET_KEY=secretref:jwt-secret FLASK_ENV=production FLASK_APP=main.py \
  --ingress external --target-port 5000 --cpu 1.0 --memory 2Gi --min-replicas 1 --max-replicas 3
```

Retrieve the application URL:
```bash
APP_URL=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "configuration.ingress.fqdn" --output tsv)
echo "https://$APP_URL"
```

## 4. Verify Deployment
```bash
curl -f https://$APP_URL/
```

## 5. Automated Script
An automated version of these steps is available in [`azure-deploy-script.sh`](azure-deploy-script.sh). Run:
```bash
./azure-deploy-script.sh
```

## 6. Cleanup
Remove all created Azure resources when no longer needed:
```bash
./azure-cleanup-script.sh
```
