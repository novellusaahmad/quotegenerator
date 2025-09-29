# Deploy to Azure Container Apps with CircleCI

This guide describes how to build a container image, push it to Azure Container Registry (ACR), and deploy/update an Azure Container App using CircleCI.

## Prerequisites
- Azure subscription and a resource group.
- Azure Container Apps enabled in the subscription.
- Azure resources provisioned (or to be provisioned ahead of time):
  - Azure Container Apps Environment (ACA Environment)
  - Azure Container Registry (ACR)
- A Dockerfile in the repository root (or update paths accordingly).

## 1) Create a Service Principal
Create a service principal with permissions to push to ACR and manage resources in your Resource Group.

```bash
az ad sp create-for-rbac \
  --name "<sp-name>" \
  --role owner \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>

# Grant ACR push rights (if not covered by the above scope/role):
az role assignment create \
  --assignee <APP_ID> \
  --role AcrPush \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.ContainerRegistry/registries/<ACR_NAME>
```

Record the following outputs/values for CircleCI:
- `AZURE_CLIENT_ID` = `<APP_ID>`
- `AZURE_CLIENT_SECRET` = `<PASSWORD>`
- `AZURE_TENANT_ID` = `<TENANT>`
- `AZURE_SUBSCRIPTION_ID` = your subscription ID

## 2) Prepare Azure Resources
- Ensure ACR exists: `<ACR_NAME>` and note its login server: `<ACR_NAME>.azurecr.io`.
- Ensure ACA Environment exists: `<AZURE_CONTAINERAPPS_ENV>`.
- Ensure a Resource Group exists: `<AZURE_RESOURCE_GROUP>`.

You may create the Container App via the pipeline on first deploy; it will detect absence and create it.

## 3) Add Environment Variables in CircleCI
In your CircleCI project settings → Environment Variables, add:

- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `AZURE_CONTAINERAPPS_ENV`
- `AZURE_CONTAINERAPP_NAME`
- `ACR_NAME`
- `ACR_LOGIN_SERVER` (e.g., `myacr.azurecr.io`)
- Optional runtime variables:
  - `CONTAINER_PORT` (default `8080`)
  - `CPU`, `MEMORY`, `MIN_REPLICAS`, `MAX_REPLICAS` (not used by default config but easy to add)

## 4) CircleCI Pipeline
This repo includes a minimal pipeline at `.circleci/config.yml` which:
- Installs Azure CLI and the `containerapp` extension.
- Logs in to Azure using the service principal.
- Logs in to ACR.
- Builds a Docker image, tags it with the short commit SHA and `latest`.
- Pushes both tags to ACR.
- Creates the Container App if missing; otherwise updates its image.
- Prints the public FQDN of the app.

Trigger: runs on pushes to the `main` branch. Adjust as needed under `workflows`.

## 5) Local Validation (optional)
Before pushing, you can validate credentials and resources locally:

```bash
az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
az account set --subscription $AZURE_SUBSCRIPTION_ID
az acr login --name $ACR_NAME
az containerapp env show -n $AZURE_CONTAINERAPPS_ENV -g $AZURE_RESOURCE_GROUP
```

## 6) First Deploy
- Push a commit to `main` (or change the branch filter to suit your flow).
- Watch the CircleCI job; on success it outputs the app URL (FQDN).

## 7) Common Adjustments
- App port: set `CONTAINER_PORT` in CircleCI if not `8080`.
- Secrets and env vars:
  - Use `az containerapp secret set` and `az containerapp update --set-env-vars KEY=secretref:KEY` for sensitive values.
  - Alternatively, extend the pipeline to pass environment variables directly on create/update.
- Scaling/resources:
  - Add `--min-replicas/--max-replicas`, `--cpu`, `--memory` to the `az containerapp update` command.
- Deploy-by-tag or approvals:
  - Add filters for Git tags and approval jobs in the workflow for staging/production gates.

## 8) Troubleshooting
- Image pull errors: ensure ACR permissions (AcrPush) and correct `ACR_LOGIN_SERVER`.
- App not reachable: confirm ingress is enabled and the port matches your app.
- Extension issues: rerun `az extension add --name containerapp` or `az extension update --name containerapp`.
- Logs: `az containerapp logs show -n $AZURE_CONTAINERAPP_NAME -g $AZURE_RESOURCE_GROUP --follow`.

---

With the above in place, each push to `main` will build, push, and deploy your app to Azure Container Apps via CircleCI.

