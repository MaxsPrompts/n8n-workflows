// main.bicep
@description('The location for all resources.')
param location string = resourceGroup().location

@description('The name of the App Service Plan.')
param appServicePlanName string = 'asp-${uniqueString(resourceGroup().id)}'

@description('The name of the Web App for the N8N Workflow Generator.')
param webAppName string = 'app-${uniqueString(resourceGroup().id)}'

@description('The Docker image for the N8N Workflow Generator (e.g., yourdockerhubusername/repository:tag).')
param generatorImageName string // Example: 'yourusername/n8n-workflow-generator:latest'

@description('OpenAI API Key.')
@secure()
param openAiApiKey string

@description('(Optional) URL of your n8n instance for auto-import.')
param n8nUrl string = ''

@description('(Optional) N8N API Key for auto-import.')
@secure()
param n8nApiKey string = ''

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1' // Basic tier, suitable for small apps. Consider F1 for Free.
    tier: 'Basic'
  }
  kind: 'linux' // Required for Linux containers
  properties: {
    reserved: true // Required for Linux App Service Plan
  }
}

// Web App for Containers (N8N Workflow Generator)
resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  kind: 'app,linux,container'
  identity: {
    type: 'SystemAssigned' // Optional: for managed identity if needed later
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${generatorImageName}' // Specifies Docker container
      alwaysOn: true // Recommended for web apps to keep them responsive
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false' // Not using built-in persistent storage for the app itself
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: '' // Not needed for Docker Hub public images
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_USERNAME'
          value: '' // Not needed for Docker Hub public images
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
          value: '' // Not needed for Docker Hub public images
        }
        {
          name: 'OPENAI_API_KEY'
          value: openAiApiKey
        }
        {
          name: 'N8N_URL'
          value: n8nUrl
        }
        {
          name: 'N8N_API_KEY'
          value: n8nApiKey
        }
        {
          name: 'FLASK_DEBUG'
          value: '0'
        }
        {
          name: 'PYTHONUNBUFFERED'
          value: '1'
        }
        {
          name: 'WEBSITES_PORT' // Tells App Service which port the container is listening on
          value: '5000'
        }
      ]
    }
    httpsOnly: true // Enforce HTTPS
  }
}

// Placeholder for deploying n8n as a separate Azure Container Instance or Web App for Containers
/*
// Example: n8n as an Azure Container Instance (ACI)
// This would require more parameters (e.g., n8n image, encryption key, volume mount details for data)
// and potentially a VNet integration if n8n needs to be private.

param n8nContainerName string = 'n8n-container-${uniqueString(resourceGroup().id)}'
param n8nImage string = 'n8nio/n8n:latest'
@secure()
param n8nEncryptionKey string

resource n8nFileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2021-09-01' = {
  // ... definition for Azure File Share for n8n data persistence ...
}

resource n8nContainerGroup 'Microsoft.ContainerInstance/containerGroups@2021-10-01' = {
  name: n8nContainerName
  location: location
  properties: {
    containers: [
      {
        name: 'n8n'
        properties: {
          image: n8nImage
          ports: [
            {
              port: 5678
              protocol: 'TCP'
            }
          ]
          environmentVariables: [
            {
              name: 'N8N_ENCRYPTION_KEY'
              secureValue: n8nEncryptionKey
            }
            {
              name: 'GENERIC_TIMEZONE'
              value: 'Europe/Berlin' // Or make it a parameter
            }
            // ... other n8n env vars ...
          ]
          resources: {
            requests: {
              cpu: 1.0
              memoryInGB: 1.5
            }
          }
          volumeMounts: [
            {
              name: 'n8ndata'
              mountPath: '/home/node/.n8n'
            }
          ]
        }
      }
    ]
    osType: 'Linux'
    restartPolicy: 'OnFailure'
    ipAddress: {
      type: 'Public' // Or 'Private' if within a VNet
      ports: [
        {
          port: 5678
          protocol: 'TCP'
        }
      ]
      // dnsNameLabel: 'n8n-instance-${uniqueString(resourceGroup().id)}' // Public DNS if ipAddress.type is Public
    }
    volumes: [
      {
        name: 'n8ndata'
        azureFile: {
          shareName: n8nFileShare.name // Reference to Azure File Share
          storageAccountName: split(n8nFileShare.id, '/')[8] // Extract storage account name
          // storageAccountKey: listKeys(storageAccount.id, storageAccount.apiVersion).keys[0].value // If using storage account key
        }
      }
    ]
  }
}
*/

output generatorWebAppName string = webApp.name
output generatorWebAppHostname string = webApp.properties.defaultHostName
