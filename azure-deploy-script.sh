#!/bin/bash

# Azure Container Apps Deployment Script
# Novellus Loan Management System
# 
# This script automates the complete deployment process to Azure Container Apps
# Run: ./azure-deploy-script.sh

set -e  # Exit on error

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

# Configuration - Edit these values for your deployment
read -p "Enter your Azure Subscription ID: " SUBSCRIPTION_ID
read -p "Enter Resource Group name (default: novellus-rg): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-novellus-rg}

read -p "Enter Azure region (default: eastus): " LOCATION
LOCATION=${LOCATION:-eastus}

read -p "Enter Container Registry name (default: novelluscr): " ACR_NAME
ACR_NAME=${ACR_NAME:-novelluscr}

read -p "Enter App name (default: novellus-loan-calculator): " APP_NAME
APP_NAME=${APP_NAME:-novellus-loan-calculator}

read -p "Enter Database server name (default: novellus-db-server): " DB_SERVER_NAME
DB_SERVER_NAME=${DB_SERVER_NAME:-novellus-db-server}

read -p "Enter Database admin password: " -s DB_PASSWORD
echo

CONTAINER_ENV="novellus-env"
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
az login

# Set subscription
az account set --subscription $SUBSCRIPTION_ID

# Step 1: Create Resource Group
echo -e "${YELLOW}Step 1: Creating Resource Group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION
echo -e "${GREEN}✅ Resource group created${NC}"

# Step 2: Create Container Registry
echo -e "${YELLOW}Step 2: Creating Azure Container Registry...${NC}"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
echo -e "${GREEN}✅ Container Registry created: $ACR_SERVER${NC}"

# Step 3: Create PostgreSQL Database
echo -e "${YELLOW}Step 3: Creating PostgreSQL Database...${NC}"
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

# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --database-name $DB_NAME

# Configure firewall
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

DB_HOST=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "fullyQualifiedDomainName" --output tsv)
DATABASE_URL="postgresql://novellus_admin:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME"
echo -e "${GREEN}✅ Database created and configured${NC}"

# Step 4: Create Container Apps Environment
echo -e "${YELLOW}Step 4: Creating Container Apps Environment...${NC}"
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App

az containerapp env create \
  --name $CONTAINER_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

echo -e "${GREEN}✅ Container Apps environment created${NC}"

# Step 5: Build and Push Docker Image
echo -e "${YELLOW}Step 5: Building and pushing Docker image...${NC}"

# Build image
docker build -t $ACR_SERVER/novellus-loan-calculator:latest .

# Login to ACR and push
az acr login --name $ACR_NAME
docker push $ACR_SERVER/novellus-loan-calculator:latest

echo -e "${GREEN}✅ Docker image built and pushed${NC}"

# Step 6: Deploy Container App
echo -e "${YELLOW}Step 6: Deploying Container App...${NC}"

# Generate secrets
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
  --secrets \
    database-url="$DATABASE_URL" \
    session-secret="$SESSION_SECRET" \
    jwt-secret="$JWT_SECRET" \
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