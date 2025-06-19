# Railway Deployment Guide

This app consists of a Python FastAPI backend and Vue.js frontend that need to be deployed as separate services on Railway.

## Deployment Steps

### 1. Create Two Services on Railway

In your Railway project, create two separate services from the same GitHub repository:

#### Backend Service:
1. Create a new service from your GitHub repo
2. In the service settings, go to the **Build** tab
3. Set the **Root Directory** to: `Apps/coin-toss/backend`
4. Railway will automatically detect Python and use requirements.txt

#### Frontend Service:
1. Create another new service from the same GitHub repo
2. In the service settings, go to the **Build** tab
3. Set the **Root Directory** to: `Apps/coin-toss/frontend`
4. Railway will use the nixpacks.toml configuration

### 2. Configure Environment Variables

#### Backend Service Variables:
```
FRONTEND_URL=${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```
Note: Replace "Frontend" with the actual name of your frontend service in Railway

#### Frontend Service Variables:
```
VITE_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
```
Note: Replace "Backend" with the actual name of your backend service in Railway

### 3. Deploy Order

Railway will automatically handle the deployment order based on the reference variables. The referenced service (backend) will deploy first.

## Local Development

For local development, the app will default to:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

No environment variables are needed for local development.

## Troubleshooting

1. **CORS Errors**: Make sure the FRONTEND_URL environment variable is correctly set in the backend service
2. **API Connection Failed**: Verify the VITE_API_URL is correctly set in the frontend service
3. **Build Failures**: Check that the root directories are correctly set for each service