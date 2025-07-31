#!/bin/bash

# Azure Resources Cleanup Script
# Novellus Loan Management System
# 
# This script removes all Azure resources created for the deployment
# WARNING: This will delete all data and cannot be undone!

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}⚠️  Azure Resources Cleanup Script${NC}"
echo -e "${RED}This will DELETE ALL Azure resources for Novellus Loan Calculator${NC}"
echo "=================================================================="

# Get resource group name
read -p "Enter Resource Group name to delete (default: novellus-rg): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-novellus-rg}

echo ""
echo -e "${YELLOW}Resources that will be DELETED:${NC}"
echo "- Resource Group: $RESOURCE_GROUP"
echo "- All resources within this group including:"
echo "  * Container Apps"
echo "  * Container Registry"
echo "  * PostgreSQL Database (ALL DATA WILL BE LOST)"
echo "  * Container Apps Environment"
echo "  * Log Analytics Workspace"
echo "  * Application Insights"
echo ""

echo -e "${RED}⚠️  THIS CANNOT BE UNDONE!${NC}"
echo ""

read -p "Type 'DELETE' to confirm deletion: " CONFIRMATION
if [[ "$CONFIRMATION" != "DELETE" ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

echo ""
read -p "Are you absolutely sure? Type 'YES' to proceed: " FINAL_CONFIRMATION
if [[ "$FINAL_CONFIRMATION" != "YES" ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

echo ""
echo -e "${YELLOW}Logging into Azure...${NC}"
az login

echo -e "${YELLOW}Deleting Resource Group: $RESOURCE_GROUP${NC}"
echo "This may take several minutes..."

az group delete --name $RESOURCE_GROUP --yes --no-wait

echo -e "${GREEN}✅ Deletion initiated${NC}"
echo ""
echo "The resource group deletion has been started in the background."
echo "You can check the status in the Azure Portal or with:"
echo "az group show --name $RESOURCE_GROUP"
echo ""
echo "All resources will be permanently deleted within 10-15 minutes."