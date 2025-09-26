#!/bin/bash

# Azure Container Apps Deployment Script
# Novellus Loan Management System
# 
# This script automates the complete deployment process to Azure Container Apps
# Run: ./azure-deploy-script.sh

set -e  # Exit on error
set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Novellus Loan Calculator - Azure Deployment Script${NC}"
echo "=================================================="

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Configuration - Defaults (can override via env or prompts)
read -p "Enter your Azure Subscription ID: " SUBSCRIPTION_ID
read -p "Enter Resource Group name (default: rg-crm-staging): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-rg-crm-staging}

read -p "Enter Azure region (default: uksouth): " LOCATION
LOCATION=${LOCATION:-uksouth}

read -p "Enter Container Registry name (default: applications): " ACR_NAME
ACR_NAME=${ACR_NAME:-applications}

read -p "Enter App name (default: novellus-loan-calculator): " APP_NAME
APP_NAME=${APP_NAME:-novellus-loan-calculator}

read -p "Enter Container Apps Environment name (default: novellus-env): " CONTAINER_ENV
CONTAINER_ENV=${CONTAINER_ENV:-novellus-env}

read -p "App container port (default: 5000): " TARGET_PORT
TARGET_PORT=${TARGET_PORT:-5000}

# Database values (only used if creating managed Postgres)
read -p "Enter Database server name (default: novellus-db-server): " DB_SERVER_NAME
DB_SERVER_NAME=${DB_SERVER_NAME:-novellus-db-server}

read -p "Enter Database admin password (leave empty to skip DB creation): " -s DB_PASSWORD || true
echo
DB_NAME="novellus_loans"

echo -e "${BLUE}Configuration:${NC}"
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "ACR Name: $ACR_NAME"
echo "App Name: $APP_NAME"
echo "DB Server: $DB_SERVER_NAME"
echo "Container Environment: $CONTAINER_ENV"
echo ""

read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

# Login to Azure
echo -e "${YELLOW}Logging into Azure...${NC}"
if [[ -n "$AZURE_CLIENT_ID" && -n "$AZURE_CLIENT_SECRET" && -n "$AZURE_TENANT_ID" ]]; then
  echo -e "${BLUE}Using service principal credentials from environment${NC}"
  az login --service-principal \
    -u "$AZURE_CLIENT_ID" \
    -p "$AZURE_CLIENT_SECRET" \
    --tenant "$AZURE_TENANT_ID"
else
  echo -e "${BLUE}Using device code flow (interactive)${NC}"
  az login --use-device-code
fi

# Set subscription
az account set --subscription $SUBSCRIPTION_ID

# Step 1: Ensure Resource Group exists
echo -e "${YELLOW}Step 1: Ensuring Resource Group...${NC}"
az group show --name $RESOURCE_GROUP >/dev/null 2>&1 || az group create --name $RESOURCE_GROUP --location $LOCATION
echo -e "${GREEN}✅ Resource group ready${NC}"

# Step 2: Ensure Container Registry exists and login
echo -e "${YELLOW}Step 2: Ensuring Azure Container Registry...${NC}"
if ! az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP >/dev/null 2>&1; then
  az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true
fi
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)

# Prefer SP-based az acr login; fallback to admin creds via docker login
if ! az acr login --name "$ACR_NAME" >/dev/null 2>&1; then
  echo -e "${YELLOW}az acr login failed; trying admin credentials via docker login...${NC}"
  ADMIN_ENABLED=$(az acr show -n "$ACR_NAME" --query 'adminUserEnabled' -o tsv)
  if [ "$ADMIN_ENABLED" != "true" ]; then
    az acr update -n "$ACR_NAME" --admin-enabled true >/dev/null
  fi
  ACR_USER=$(az acr credential show -n "$ACR_NAME" --query username -o tsv)
  ACR_PASS=$(az acr credential show -n "$ACR_NAME" --query 'passwords[0].value' -o tsv)
  echo "$ACR_PASS" | docker login "$ACR_SERVER" -u "$ACR_USER" --password-stdin
fi
echo -e "${GREEN}✅ Container Registry ready: $ACR_SERVER${NC}"

# Step 3: Create PostgreSQL Database (idempotent, optional)
echo -e "${YELLOW}Step 3: Creating PostgreSQL Database...${NC}"

echo -e "${YELLOW}Checking the existence of the resource group '$RESOURCE_GROUP'...${NC}"
RG_EXISTS=$(az group exists --name "$RESOURCE_GROUP")
echo -e "Resource group '$RESOURCE_GROUP' exists ? : $RG_EXISTS"

DB_SERVER_EXISTS=false
if az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "$DB_SERVER_NAME" >/dev/null 2>&1; then
  DB_SERVER_EXISTS=true
  echo -e "${BLUE}PostgreSQL server '$DB_SERVER_NAME' already exists. Skipping server creation.${NC}"
fi

if [ -n "$DB_PASSWORD" ] && [ "$DB_SERVER_EXISTS" != true ]; then
  az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --location $LOCATION \
    --admin-user novellus_admin \
    --admin-password "$DB_PASSWORD" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --version 14 \
    --storage-size 32 \
    --high-availability Disabled \
    --zone 1
elif [ -n "$DB_PASSWORD" ]; then
  echo -e "${YELLOW}Skipping server creation as it already exists.${NC}"
fi

# Create database if not exists (only when DB configured)
if [ -n "$DB_PASSWORD" ] && ! az postgres flexible-server db show \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --database-name $DB_NAME >/dev/null 2>&1; then
  az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --database-name $DB_NAME
elif [ -n "$DB_PASSWORD" ]; then
  echo -e "${BLUE}Database '$DB_NAME' already exists. Skipping database creation.${NC}"
fi

# Configure firewall rule (idempotent; only when DB configured)
if [ -n "$DB_PASSWORD" ] && ! az postgres flexible-server firewall-rule show \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --rule-name AllowAzureServices >/dev/null 2>&1; then
  az postgres flexible-server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --rule-name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
elif [ -n "$DB_PASSWORD" ]; then
  echo -e "${BLUE}Firewall rule 'AllowAzureServices' already exists. Skipping.${NC}"
fi

if [ -n "$DB_PASSWORD" ]; then
  DB_HOST=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "fullyQualifiedDomainName" --output tsv)
  DATABASE_URL="postgresql://novellus_admin:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME"
  echo -e "${GREEN}✅ Database created/configured (idempotent)${NC}"
else
  echo -e "${YELLOW}Skipping managed PostgreSQL creation; no DB password provided.${NC}"
fi

# Step 4: Ensure Container Apps Environment exists (no Log Analytics)
echo -e "${YELLOW}Step 4: Ensuring Container Apps Environment...${NC}"
az extension add --name containerapp || az extension update --name containerapp
az provider register --namespace Microsoft.App

if ! az containerapp env show -n "$CONTAINER_ENV" -g "$RESOURCE_GROUP" >/dev/null 2>&1; then
  az containerapp env create \
    --name $CONTAINER_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION
  echo -e "${GREEN}✅ Container Apps environment created${NC}"
else
  echo -e "${BLUE}Container Apps environment '$CONTAINER_ENV' already exists. Skipping creation.${NC}"
fi

# Step 5: Build and Push Docker Image
echo -e "${YELLOW}Step 5: Building and pushing Docker image...${NC}"

# Build image (tag with commit short SHA if available)
IMAGE_TAG=${CIRCLE_SHA1:0:7}
IMAGE_TAG=${IMAGE_TAG:-latest}
docker build -t $ACR_SERVER/novellus-loan-calculator:$IMAGE_TAG -t $ACR_SERVER/novellus-loan-calculator:latest .

# Push images (already logged in earlier)
docker push $ACR_SERVER/novellus-loan-calculator:$IMAGE_TAG
docker push $ACR_SERVER/novellus-loan-calculator:latest

echo -e "${GREEN}✅ Docker image built and pushed${NC}"

# Step 6: Deploy/Update Container App
echo -e "${YELLOW}Step 6: Deploying Container App...${NC}"

# Generate secrets
SESSION_SECRET=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

if ! az containerapp show -n "$APP_NAME" -g "$RESOURCE_GROUP" >/dev/null 2>&1; then
  az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_ENV \
    --image $ACR_SERVER/novellus-loan-calculator:$IMAGE_TAG \
    --registry-server $ACR_SERVER \
    --ingress external \
    --target-port $TARGET_PORT \
    --cpu 1.0 \
    --memory 2Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    $( [ -n "$DATABASE_URL" ] && echo --secrets database-url="$DATABASE_URL" ) \
    $( [ -n "$DATABASE_URL" ] && echo --env-vars DATABASE_URL=secretref:database-url ) \
    --env-vars SESSION_SECRET=$SESSION_SECRET JWT_SECRET_KEY=$JWT_SECRET FLASK_ENV=production FLASK_APP=main.py
else
  az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_SERVER/novellus-loan-calculator:$IMAGE_TAG \
    --set-env-vars SESSION_SECRET=$SESSION_SECRET JWT_SECRET_KEY=$JWT_SECRET \
    $( [ -n "$DATABASE_URL" ] && echo --set-env-vars DATABASE_URL=secretref:database-url )
fi

echo -e "${GREEN}✅ Container App deployed${NC}"

# Get application URL
APP_URL=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "configuration.ingress.fqdn" --output tsv)

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================================="
echo -e "${BLUE}Application URL: https://$APP_URL${NC}"
echo -e "${BLUE}Database Host: $DB_HOST${NC}"
echo -e "${BLUE}Resource Group: $RESOURCE_GROUP${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Visit your application at: https://$APP_URL"
echo "2. Set up monitoring in Azure Portal"
echo "3. Configure custom domain (if needed)"
echo "4. Set up CI/CD pipeline"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "View logs: az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo "Scale app: az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --min-replicas 2"
echo "Update image: az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --image $ACR_SERVER/novellus-loan-calculator:new-tag"
echo ""
echo "Deployment script completed successfully!"
