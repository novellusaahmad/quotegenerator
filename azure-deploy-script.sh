#!/bin/bash

# Azure Container Apps Deployment Script (Managed DB Only)
# Novellus Loan Management System

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Novellus Loan Calculator - Azure Deployment (Managed DB Only)${NC}"
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

SUBSCRIPTION_ID="c61a3539-0683-4a3d-a9ba-9d56c71bb9ec"
read -p "Resource Group [rg-crm-staging]: " RESOURCE_GROUP; RESOURCE_GROUP=${RESOURCE_GROUP:-rg-crm-staging}
read -p "Azure region [uksouth]: " LOCATION; LOCATION=${LOCATION:-uksouth}
read -p "ACR name [applications]: " ACR_NAME; ACR_NAME=${ACR_NAME:-applications}
read -p "App name [novellus-loan-calculator]: " APP_NAME; APP_NAME=${APP_NAME:-novellus-loan-calculator}
read -p "ACA environment [novellus-env]: " CONTAINER_ENV; CONTAINER_ENV=${CONTAINER_ENV:-novellus-env}
read -p "App port [5000]: " TARGET_PORT; TARGET_PORT=${TARGET_PORT:-5000}

DB_NAME="novellus_loans"
read -p "DB server name [loancalculator-db-server]: " DB_SERVER_NAME; DB_SERVER_NAME=${DB_SERVER_NAME:-loancalculator-db-server}
# Networking exposure for DB server: world|azure|custom
read -p "DB firewall scope [azure] (world/azure/custom): " DB_FIREWALL_SCOPE; DB_FIREWALL_SCOPE=${DB_FIREWALL_SCOPE:-azure}
if [ "$DB_FIREWALL_SCOPE" = "custom" ]; then
  read -p "Comma-separated IP ranges (e.g. 1.2.3.4-1.2.3.4,5.6.7.8-5.6.7.8): " DB_CUSTOM_IPS; DB_CUSTOM_IPS=${DB_CUSTOM_IPS:-}
fi
# Use fixed managed DB admin password for novellus_admin
DB_PASSWORD='lendingdynamics987654321'
# Trim any accidental whitespace and confirm non-empty (debug)
DB_PASSWORD=$(printf %s "$DB_PASSWORD" | sed 's/^[[:space:]]\+//; s/[[:space:]]\+$//')
echo "DBG: DB_PASSWORD length=$(printf %s "$DB_PASSWORD" | wc -c | tr -d ' ')"

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

echo -e "${YELLOW}Logging into Azure and selecting subscription...${NC}"
az login --use-device-code >/dev/null
az account set --subscription "$SUBSCRIPTION_ID"

# Step 1: Ensure Resource Group exists
echo -e "${YELLOW}Step 1: Ensuring Resource Group...${NC}"
az group show --name $RESOURCE_GROUP >/dev/null 2>&1 || az group create --name $RESOURCE_GROUP --location $LOCATION
echo -e "${GREEN}✅ Resource group ready${NC}"

echo -e "${YELLOW}Step 2: Ensuring ACR...${NC}"
az acr show -n "$ACR_NAME" -g "$RESOURCE_GROUP" >/dev/null 2>&1 || az acr create -n "$ACR_NAME" -g "$RESOURCE_GROUP" --sku Basic --admin-enabled true >/dev/null
ACR_SERVER=$(az acr show -n "$ACR_NAME" -g "$RESOURCE_GROUP" --query loginServer -o tsv)
az acr login -n "$ACR_NAME" >/dev/null 2>&1 || {
  ACR_USER=$(az acr credential show -n "$ACR_NAME" --query username -o tsv)
  ACR_PASS=$(az acr credential show -n "$ACR_NAME" --query 'passwords[0].value' -o tsv)
  echo "$ACR_PASS" | docker login "$ACR_SERVER" -u "$ACR_USER" --password-stdin
}
echo -e "${GREEN}✅ Container Registry ready: $ACR_SERVER${NC}"

## Step 3: Managed DB provisioning
echo -e "${YELLOW}Step 3: Managed DB provisioning...${NC}"

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

if [ -n "$DB_PASSWORD" ]; then
  echo -e "${YELLOW}Configuring PostgreSQL firewall (${DB_FIREWALL_SCOPE})...${NC}"
  if [ "$DB_FIREWALL_SCOPE" = "world" ]; then
    az postgres flexible-server firewall-rule create \
      --resource-group $RESOURCE_GROUP \
      --name $DB_SERVER_NAME \
      --rule-name AllowAll \
      --start-ip-address 0.0.0.0 \
      --end-ip-address 255.255.255.255 >/dev/null 2>&1 || true
    echo -e "${GREEN}✅ DB open to world (NOT recommended for prod)${NC}"
  elif [ "$DB_FIREWALL_SCOPE" = "azure" ]; then
    az postgres flexible-server firewall-rule create \
      --resource-group $RESOURCE_GROUP \
      --name $DB_SERVER_NAME \
      --rule-name AllowAzureServices \
      --start-ip-address 0.0.0.0 \
      --end-ip-address 0.0.0.0 >/dev/null 2>&1 || true
    echo -e "${GREEN}✅ DB open to Azure services only${NC}"
  elif [ "$DB_FIREWALL_SCOPE" = "custom" ] && [ -n "$DB_CUSTOM_IPS" ]; then
    IFS=',' read -r -a RANGES <<< "$DB_CUSTOM_IPS"
    i=1
    for r in "${RANGES[@]}"; do
      start_ip=${r%-*}
      end_ip=${r#*-}
      az postgres flexible-server firewall-rule create \
        --resource-group $RESOURCE_GROUP \
        --name $DB_SERVER_NAME \
        --rule-name CustomRange$i \
        --start-ip-address "$start_ip" \
        --end-ip-address "$end_ip" >/dev/null 2>&1 || true
      i=$((i+1))
    done
    echo -e "${GREEN}✅ DB firewall configured for custom ranges${NC}"
  else
    echo -e "${YELLOW}No firewall changes applied (unknown scope)${NC}"
  fi
fi

if [ -n "$DB_PASSWORD" ]; then
  DB_HOST=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "fullyQualifiedDomainName" --output tsv)
  echo "DBG: composing DATABASE_URL..."
  ENC_DB_PASSWORD=$(DB_PASSWORD="$DB_PASSWORD" python3 - << 'PY'
import os, urllib.parse
pwd = os.environ.get('DB_PASSWORD', '')
print(urllib.parse.quote(pwd.strip(), safe=''))
PY
)
  echo "DBG: Encoded password length=$(printf %s "$ENC_DB_PASSWORD" | wc -c | tr -d ' ')"
  DATABASE_URL="postgresql://novellus_admin:${ENC_DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"
  if ! echo "$DATABASE_URL" | grep -qE 'postgresql:\/\/novellus_admin:[^@]+@'; then
    echo -e "${RED}Composed DATABASE_URL is missing password; aborting.${NC}"; exit 1
  fi
  echo -e "${GREEN}✅ Managed PostgreSQL configured${NC}"
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
echo -e "${YELLOW}Step 4: Building and pushing Docker image...${NC}"

# Build image tag from git commit if available, else latest
if git rev-parse --short HEAD >/dev/null 2>&1; then
  IMAGE_TAG=$(git rev-parse --short HEAD)
else
  IMAGE_TAG="latest"
fi
docker build -t "$ACR_SERVER/novellus-loan-calculator:$IMAGE_TAG" -t "$ACR_SERVER/novellus-loan-calculator:latest" .

# Push images (already logged in earlier)
docker push "$ACR_SERVER/novellus-loan-calculator:$IMAGE_TAG"
docker push "$ACR_SERVER/novellus-loan-calculator:latest"

echo -e "${GREEN}✅ Docker image built and pushed${NC}"

# Step 6: Deploy/Update Container App
echo -e "${YELLOW}Step 5: Deploying Container App...${NC}"

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
    $( [ -n "$DATABASE_URL" ] && echo --env-vars DATABASE_URL=secretref:database-url SQLALCHEMY_DATABASE_URI=secretref:database-url ) \
    --env-vars SESSION_SECRET=$SESSION_SECRET JWT_SECRET_KEY=$JWT_SECRET FLASK_ENV=production FLASK_APP=main.py
else
  # Ensure secret is set in a CLI-version-compatible way
  if [ -n "$DATABASE_URL" ]; then
    az containerapp secret set \
      --name "$APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --secrets database-url="$DATABASE_URL"
  fi

  az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_SERVER/novellus-loan-calculator:$IMAGE_TAG \
    --set-env-vars SESSION_SECRET=$SESSION_SECRET JWT_SECRET_KEY=$JWT_SECRET \
    $( [ -n "$DATABASE_URL" ] && echo --set-env-vars DATABASE_URL=secretref:database-url SQLALCHEMY_DATABASE_URI=secretref:database-url )

echo -e "${YELLOW}Restarting revision to apply configuration...${NC}"
az containerapp revision restart -n "$APP_NAME" -g "$RESOURCE_GROUP" >/dev/null 2>&1 || true
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
echo -e "${YELLOW}Post-deploy: initializing database inside the container...${NC}"

# Helpers to robustly discover revision and replica
RETRIES=36; SLEEP=5
get_latest_revision() {
  local rev
  rev=$(az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.latestRevisionName" -o tsv 2>/dev/null || true)
  [ -n "$rev" ] && [ "$rev" != "null" ] && { echo "$rev"; return 0; }
  rev=$(az containerapp revision list --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "sort_by(@,&properties.createdTime)[-1].name" -o tsv 2>/dev/null || true)
  [ -n "$rev" ] && [ "$rev" != "null" ] && { echo "$rev"; return 0; }
  az containerapp revision restart -n "$APP_NAME" -g "$RESOURCE_GROUP" >/dev/null 2>&1 || true
  sleep 5
  rev=$(az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.latestRevisionName" -o tsv 2>/dev/null || true)
  [ -n "$rev" ] && [ "$rev" != "null" ] && { echo "$rev"; return 0; }
  echo ""; return 1
}

echo -e "${BLUE}Discovering latest revision...${NC}"
LATEST_REV=""
for i in $(seq 1 $RETRIES); do
  LATEST_REV=$(get_latest_revision || true)
  [ -n "$LATEST_REV" ] && [ "$LATEST_REV" != "null" ] && break
  echo -e "${YELLOW}Waiting for revision ($i/$RETRIES)...${NC}"; sleep $SLEEP
done

if [ -z "$LATEST_REV" ] || [ "$LATEST_REV" = "null" ]; then
  echo -e "${RED}❌ Could not determine a revision. Showing app status and exiting.${NC}"
  az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" || true
  exit 1
fi

echo -e "${BLUE}Waiting for a ready replica in $LATEST_REV...${NC}"
REPLICA=""
for i in $(seq 1 $RETRIES); do
  REPLICA=$(az containerapp replica list --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --revision "$LATEST_REV" --query "[0].name" -o tsv 2>/dev/null || true)
  if [ -n "$REPLICA" ] && [ "$REPLICA" != "null" ]; then break; fi
  STATUS=$(az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.runningStatus" -o tsv 2>/dev/null || true)
  if [ "$STATUS" = "Stopped" ] || [ "$STATUS" = "Failed" ]; then
    echo -e "${YELLOW}App status: $STATUS. Triggering restart...${NC}"; az containerapp revision restart -n "$APP_NAME" -g "$RESOURCE_GROUP" >/dev/null 2>&1 || true
  fi
  echo -e "${YELLOW}Waiting for replica ($i/$RETRIES)...${NC}"; sleep $SLEEP
done

if [ -z "$REPLICA" ] || [ "$REPLICA" = "null" ]; then
  echo -e "${RED}❌ No replica found for revision $LATEST_REV. Showing recent logs.${NC}"
  az containerapp logs show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --tail 100 || true
  exit 1
fi

echo -e "${BLUE}Running database initialization on revision ${LATEST_REV}, replica ${REPLICA}...${NC}"

# Exec into the container and run database initialization and connection test
set +e
az containerapp exec \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --revision "$LATEST_REV" \
  --replica "$REPLICA" \
  --command \
  "/bin/sh -lc 'echo Using DATABASE_URL=\"\$DATABASE_URL\"; python database_init.py && python - <<\"PY\"\nfrom database_init import test_database_connection as t\nimport sys\nsys.exit(0 if t() else 1)\nPY\n'"
INIT_RC=$?
set -e

if [ $INIT_RC -ne 0 ]; then
  echo -e "${RED}❌ Database initialization or connection test failed. Check container logs.${NC}"
  echo "Hint: az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
  exit $INIT_RC
fi

echo -e "${GREEN}✅ Database initialized and verified successfully${NC}"
echo "Deployment script completed successfully!"
