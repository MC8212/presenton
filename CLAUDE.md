# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Presenton is an open-source AI presentation generator with a FastAPI backend (Python) and Next.js frontend (TypeScript). It supports multiple LLM providers (OpenAI, Google, Anthropic, Ollama, custom OpenAI-compatible) and image providers (DALL-E 3, Gemini Flash, Pexels, Pixabay).

## Development Commands

### Docker Development (Recommended)
```bash
# Start development stack with hot reload
docker compose up --build development

# With GPU support for Ollama
docker compose up --build development-gpu

# Access at http://localhost:5000
```

### Manual Local Development

**Backend (FastAPI):**
```bash
cd servers/fastapi
python server.py --port 8000 --reload true
```

**Frontend (Next.js):**
```bash
cd servers/nextjs
npm install
npm run dev      # Development with hot reload
npm run build    # Production build
npm run lint     # Run ESLint
```

**MCP Server:**
```bash
cd servers/fastapi
python mcp_server.py --port 8001
```

### Testing
```bash
# Frontend E2E tests (Cypress)
cd servers/nextjs
npx cypress run

# Backend tests
cd servers/fastapi
pytest
```

## Architecture

### Request Flow
```
User → Next.js (port 3000) → Nginx (port 80/5000) → FastAPI (port 8000)
                                                  → MCP Server (port 8001)
```

### Key Directories
- `servers/fastapi/` - Python backend
  - `api/v1/ppt/endpoints/` - REST API routes
  - `services/` - Business logic (LLM client, image generation, database)
  - `utils/llm_calls/` - LLM prompt orchestration
  - `models/sql/` - SQLModel database tables
- `servers/nextjs/` - TypeScript frontend
  - `app/` - Next.js App Router pages
  - `components/` - React components
  - `store/` - Redux state management
  - `presentation-templates/` - HTML/Tailwind slide templates

### Core Services
- **LLMClient** (`services/llm_client.py`) - Unified interface for all LLM providers with streaming, tool calls, and structured output
- **ImageGenerationService** (`services/image_generation_service.py`) - Multi-provider image generation
- **ConcurrentService** (`services/concurrent_service.py`) - Async task queue for background processing

### Database
SQLite by default (development), supports PostgreSQL/MySQL via `DATABASE_URL` env var. Models in `models/sql/`.

## Environment Configuration

Key variables in `.env`:
```bash
LLM=openai|google|anthropic|ollama|custom
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
CUSTOM_LLM_URL=...
IMAGE_PROVIDER=dall-e-3|gemini_flash|pexels|pixabay
CAN_CHANGE_KEYS=true|false  # Allow runtime API key changes
```

## Key Patterns

### LLM Provider Abstraction
All LLM calls go through `services/llm_client.py`. Provider-specific logic is in `utils/llm_provider.py`. Adding a new provider requires:
1. Add to `enums/llm_provider.py`
2. Implement in `services/llm_client.py`
3. Add config endpoint in `api/v1/ppt/endpoints/`
4. Update frontend in `components/[Provider]Config.tsx`

### Streaming Responses
LLM responses use Server-Sent Events (SSE) via `SSEResponse`, `SSECompleteResponse`, `SSEErrorResponse` classes.

### User Configuration
Runtime config stored in `app_data/userConfig.json`. Hierarchy: environment variables → user config file → defaults.

## API Endpoints

Main presentation endpoints:
- `POST /api/v1/ppt/presentation/generate` - Generate presentation
- `GET /api/v1/ppt/presentation/{id}` - Get presentation
- `POST /api/v1/ppt/slide/{id}/edit` - Edit slide content
- `POST /api/v1/ppt/files/upload` - Upload PPTX/PDF for template extraction

API docs available at `http://localhost:8000/docs` when backend is running.
