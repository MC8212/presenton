# Presenton Deployment Plan with OpenRouter

## Overview
Deploy Presenton locally using Docker Compose in development mode. Configure using CUSTOM LLM provider for OpenRouter compatibility.

## Prerequisites
- Docker Desktop installed and running on Windows.
- Run `docker --version` in PowerShell to verify.

## Step 1: Create .env file
Create `presenton/.env` with the following content:

```
LLM=custom
CUSTOM_LLM_URL=https://openrouter.ai/api/v1
CUSTOM_LLM_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.zB2Ur3uXOMsh1XRiNhLh0QCVGzTtVPh60ubwSkm7wr0
CUSTOM_MODEL=x-ai/grok-4.1-fast:free
CAN_CHANGE_KEYS=true
IMAGE_PROVIDER=pexels
DISABLE_ANONYMOUS_TELEMETRY=true
```

**Note:** For images:
- Pexels: Get free API key from [pexels.com/api](https://www.pexels.com/api/), add `PEXELS_API_KEY=your_key`.
- Or set `IMAGE_PROVIDER=dall-e-3` and use OpenAI key (separate from LLM).
- Access UI to set image provider/key if CAN_CHANGE_KEYS=true.

## Step 2: Deploy
Open PowerShell in workspace root (`c:/Users/mc308324/OneDrive - North Highland/NH Crowell/AI Agents/Claude/NH PPT Builder v2`).

Run:
```
cd presenton
docker compose up --build development
```

- Uses `Dockerfile.dev`, mounts source for hot-reload.
- Exposes http://localhost:5000
- Creates `./app_data` for persistence.

For GPU (if NVIDIA): `docker compose --profile development-gpu up --build`

## Step 3: Access and Configure
- Open http://localhost:5000
- Select Custom LLM if not auto-set.
- Enter details if prompted (base URL, key, model).
- Set image provider/key.

## Step 4: Test
- Generate a sample presentation.
- Later: Use your template for testing.

## Troubleshooting
- Port 5000 busy? Change in docker-compose.yml: ports: - "5001:80"
- Build fails? `docker compose down`, clean images.
- Ollama/GPU: Separate setup.

## Next
Approve plan? Changes? Ready to switch to **code** mode for any code tweaks or **orchestrator** for execution.
