#!/bin/bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
echo -e "${BLUE}Azure Container Apps Deploy (Managed DB Only)${NC}"
echo "=================================================="

Subscription and inputs
SUBSCRIPTION_ID="c61a3539-0683-4a3d-a9ba-9d56c71bb9ec"
read -p "Resource Group [rg-crm-staging]: " RG; RG=${RG:-rg-crm-staging}
read -p "Region [uksouth]: " LOC; LOC=${LOC:-uksouth}
read -p "ACR name [applications]: " ACR; ACR=${ACR:-applications}
read -p "App name [novellus-loan-calculator]: " APP; APP=${APP:-novellus-loan-calculator}
read -p "ACA environment [novellus-env]: " ENV; ENV=${ENV:-novellus-env}
read -p "App port [5000]: " PORT; PORT=${PORT:-5000}

Managed Postgres settings
DB_NAME="novellus_loans"
read -p "DB server name [novellus-db-server]: " DB_SERVER; DB_SERVER=${DB_SERVER:-novellus-db-server}
read -s -p "DB admin password (novellus_admin) [Novellus@123]: " DB_PWD; echo
DB_PWD=${DB_PWD:-Novellus@123}
if [ -z "${DB_PWD}" ]; then echo -e "${RED}DB password cannot be empty${NC}"; exit 1; fi

echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v az >/dev/null || { echo -e "${RED}Azure CLI not installed${NC}"; exit 1; }
command -v docker >/dev/null || { echo -e "${RED}Docker not installed${NC}"; exit 1; }
echo -e "${GREEN}OK${NC}"

echo -e "${YELLOW}Login + subscription...${NC}"
az login --use-device-code >/dev/null
az account set --subscription "$SUBSCRIPTION_ID"

echo -e "${YELLOW}Ensure RG/ACR/ENV...${NC}"
az group show -n "$RG" >/dev/null 2>&1 || az group create -n "$RG" -l "$LOC" >/dev/null
az acr show -n "$ACR" -g "$RG" >/dev/null 2>&1 || az acr create -n "$ACR" -g "$RG" --sku Basic --admin-enabled true >/dev/null
ACR_SERVER=$(az acr show -n "$ACR" -g "$RG" --query loginServer -o tsv)
az extension add --name containerapp >/dev/null 2>&1 || az extension update --name containerapp >/dev/null 2>&1
az provider register --namespace Microsoft.App >/dev/null 2>&1 || true
az containerapp env show -n "$ENV" -g "$RG" >/dev/null 2>&1 || az containerapp env create -n "$ENV" -g "$RG" -l "$LOC" >/dev/null

echo -e "${YELLOW}Ensure Managed Postgres server/db...${NC}"
az postgres flexible-server show -g "$RG" -n "$DB_SERVER" >/dev/null 2>&1 || az postgres flexible-server create -g "$RG" -n "$DB_SERVER" -l "$LOC" --admin-user novellus_admin --admin-password "$DB_PWD" --sku-name Standard_B1ms --tier Burstable --version 14 --storage-size 32 --high-availability Disabled --zone 1 >/dev/null
az postgres flexible-server db show -g "$RG" -s "$DB_SERVER" -d "$DB_NAME" >/dev/null 2>&1 || az postgres flexible-server db create -g "$RG" -s "$DB_SERVER" -d "$DB_NAME" >/dev/null
az postgres flexible-server firewall-rule show -g "$RG" -n "$DB_SERVER" --rule-name AllowAzureServices >/dev/null 2>&1 || az postgres flexible-server firewall-rule create -g "$RG" -n "$DB_SERVER" --rule-name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0 >/dev/null

echo -e "${YELLOW}Build DB URL (encode password)...${NC}"
ENC_PWD=$(python3 - <<PY
import urllib.parse,sys
print(urllib.parse.quote(sys.argv[1], safe=''))
PY
"$DB_PWD")
DB_HOST=$(az postgres flexible-server show -g "$RG" -n "$DB_SERVER" --query fullyQualifiedDomainName -o tsv)
DATABASE_URL="postgresql://novellus_admin:${ENC_PWD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"
echo "$DATABASE_URL" | grep -qE 'postgresql://novellus_admin:[^@]+@' || { echo -e "${RED}Bad DB URL (empty or unencoded password)${NC}"; exit 1; }

echo -e "${YELLOW}Build/push image...${NC}"
az acr login -n "$ACR" >/dev/null 2>&1 || {
ACR_USER=$(az acr credential show -n "$ACR" --query username -o tsv)
ACR_PASS=$(az acr credential show -n "$ACR" --query 'passwords[0].value' -o tsv)
echo "$ACR_PASS" | docker login "$ACR_SERVER" -u "$ACR_USER" --password-stdin
}
TAG=${CIRCLE_SHA1:0:7}; TAG=${TAG:-latest}
docker build -t "$ACR_SERVER/$APP:$TAG" -t "$ACR_SERVER/$APP:latest" .
docker push "$ACR_SERVER/$APP:$TAG"
docker push "$ACR_SERVER/$APP:latest"

echo -e "${YELLOW}Wire secret + env...${NC}"
az containerapp secret set -n "$APP" -g "$RG" --secrets database-url="$DATABASE_URL" >/dev/null
if ! az containerapp show -n "$APP" -g "$RG" >/dev/null 2>&1; then
az containerapp create -n "$APP" -g "$RG" --environment "$ENV"
--image "$ACR_SERVER/$APP:$TAG" --registry-server "$ACR_SERVER"
--ingress external --target-port "$PORT" --cpu 1.0 --memory 2Gi
--min-replicas 1 --max-replicas 3
--env-vars DATABASE_URL=secretref:database-url SQLALCHEMY_DATABASE_URI=secretref:database-url >/dev/null
else
az containerapp update -n "$APP" -g "$RG" --image "$ACR_SERVER/$APP:$TAG"
--set-env-vars DATABASE_URL=secretref:database-url SQLALCHEMY_DATABASE_URI=secretref:database-url >/dev/null
fi

echo -e "${YELLOW}Restart revision...${NC}"
az containerapp revision restart -n "$APP" -g "$RG" >/dev/null

APP_URL=$(az containerapp show -n "$APP" -g "$RG" --query properties.configuration.ingress.fqdn -o tsv)
echo -e "${GREEN}Done. App URL:${NC} https://$APP_URL"
