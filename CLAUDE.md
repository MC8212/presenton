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

## Fork Management (North Highland)

This repository is a fork of [presenton/presenton](https://github.com/presenton/presenton) with North Highland customizations.

### Branch Strategy
- **`main`** - Clean mirror of upstream `presenton/presenton` (never edit directly)
- **`nh-custom`** - North Highland customizations branch (all changes go here)

### Remote Configuration
```
origin   → https://github.com/MC8212/presenton.git (your fork)
upstream → https://github.com/presenton/presenton.git (original)
```

### Syncing with Upstream

Use the `/sync-upstream` slash command to automatically sync with upstream changes, or run manually:

```bash
# 1. Backup NH-specific data before sync
cp app_data/fastapi.db app_data/fastapi.db.pre-sync-backup

# 2. Fetch latest from upstream
git fetch upstream

# 3. Update main to match upstream
git checkout main
git merge --ff-only upstream/main
git push origin main

# 4. Rebase customizations onto updated main
git checkout nh-custom
git rebase main

# 5. Push updated customizations (force required after rebase)
git push origin nh-custom --force-with-lease
```

### Pre-Sync Checklist

Before syncing with upstream, verify these are committed or backed up:

- [ ] NH-branded templates in `presentation-templates/nh-*/`
- [ ] Custom vision service (`services/vision_llm_service.py`)
- [ ] Template provider endpoint (`api/v1/ppt/endpoints/template_providers.py`)
- [ ] Database backup (`app_data/fastapi.db`)
- [ ] User config backup (`app_data/userConfig.json`)

### Post-Sync Verification

After sync completes:

1. **Check NH templates exist:** `ls servers/nextjs/presentation-templates/nh-*`
2. **Verify custom services:** `ls servers/fastapi/services/vision_llm_service.py`
3. **Test template creation page:** Navigate to `/custom-template` and verify provider selector
4. **Test existing templates:** Generate a presentation using NH templates

### Handling Conflicts
When conflicts occur during rebase:
1. Resolve conflicts in each file, preserving NH customizations
2. `git add <resolved-file>`
3. `git rebase --continue`
4. Repeat until rebase completes

### NH Customizations
The `nh-custom` branch includes:
- Custom image provider support (OpenAI-compatible APIs like OpenRouter)
- Extended configuration options for image generation
- Claude Code configuration and slash commands
- Deployment planning documentation
- **Multi-provider template extraction** (see below)
- **Custom North Highland design templates** (see below)

### Critical Files to Preserve During Sync

When syncing with upstream, these NH-specific files/directories require special attention:

| Path | Type | Notes |
|------|------|-------|
| `servers/nextjs/presentation-templates/nh-*` | Directory | NH-branded slide templates |
| `servers/fastapi/services/vision_llm_service.py` | File | Multi-provider vision service |
| `servers/fastapi/api/v1/ppt/endpoints/template_providers.py` | File | Provider availability endpoint |
| `.claude/` | Directory | Claude Code configuration |
| `app_data/` | Directory | Runtime data (gitignored, backup separately) |

**Warning:** The `app_data/` directory contains:
- `fastapi.db` - SQLite database with saved custom templates
- `userConfig.json` - User configuration
- Generated images and exports

This directory is gitignored. For production deployments, back up `app_data/` separately.

## Multi-Provider Template Extraction

The custom template creation feature now supports multiple LLM providers instead of being hardcoded to OpenAI GPT-5.

### How It Works

When creating custom templates from PPTX/PDF files, users can select which AI provider to use for:
1. **Slide-to-HTML conversion** - Converting slide images to HTML/Tailwind code
2. **HTML-to-React conversion** - Converting HTML to React components for rendering

### Supported Providers

| Provider | Environment Variable | Model Used |
|----------|---------------------|------------|
| OpenAI | `OPENAI_API_KEY` | gpt-4o (vision) |
| Google | `GOOGLE_API_KEY` | gemini-2.0-flash |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| Custom (OpenRouter) | `CUSTOM_LLM_URL` + `CUSTOM_LLM_API_KEY` | Configurable |

### New Files Created

**Backend:**
- `services/vision_llm_service.py` - Abstraction layer for vision/multimodal LLM calls
- `api/v1/ppt/endpoints/template_providers.py` - Endpoint to get available providers

**Frontend:**
- `app/(presentation-generator)/custom-template/hooks/useTemplateProvider.ts` - Provider state hook
- `app/(presentation-generator)/custom-template/components/TemplateProviderSelector.tsx` - UI dropdown

### API Endpoints

- `GET /api/v1/ppt/template-providers/available` - Returns providers with configured API keys
- `POST /api/v1/ppt/slide-to-html/` - Now accepts optional `provider` parameter
- `POST /api/v1/ppt/html-to-react/` - Now accepts optional `provider` parameter
- `POST /api/v1/ppt/edit-html-with-images/` - Now accepts optional `provider` form field

### Configuration for Custom/OpenRouter

To use OpenRouter or another OpenAI-compatible API:
```bash
CUSTOM_LLM_URL=https://openrouter.ai/api/v1
CUSTOM_LLM_API_KEY=your-openrouter-key
CUSTOM_LLM_MODEL=google/gemini-2.0-flash-exp:free  # Must support vision
```

**Important:** The custom model must support vision/multimodal inputs for template extraction to work.

## Design Templates Architecture

Presenton uses a hierarchical template system for generating presentations.

### Template Storage Locations

| Location | Type | Version Control | Notes |
|----------|------|-----------------|-------|
| `servers/nextjs/presentation-templates/` | Built-in templates | Git tracked | Upstream templates (general, modern, standard, swift) |
| `servers/nextjs/presentation-templates/nh-*/` | NH custom templates | Git tracked | North Highland branded templates |
| Database (`app_data/fastapi.db`) | User-created templates | Not tracked | Custom templates created via UI |

### Built-in Template Structure

Each template theme has:
```
presentation-templates/
├── general/                    # General-purpose layouts
│   ├── settings.json          # Theme configuration (colors, fonts)
│   ├── IntroSlideLayout.tsx   # Slide layout components
│   └── ...
├── modern/                     # Modern theme
├── standard/                   # Standard theme
├── swift/                      # Swift theme
└── nh-brand/                   # NH-specific (to be created)
    ├── settings.json
    └── [layouts].tsx
```

### settings.json Structure

```json
{
  "name": "Theme Name",
  "description": "Theme description",
  "colorScheme": {
    "primary": "#hex",
    "secondary": "#hex",
    "background": "#hex",
    "text": "#hex"
  },
  "fonts": {
    "heading": "Font Family",
    "body": "Font Family"
  }
}
```

### Creating NH-Branded Templates

1. **From existing PPTX:** Use `/custom-template` page to extract layouts from North Highland branded PPTX files
2. **Manual creation:** Create `.tsx` files in `presentation-templates/nh-brand/`
3. **Database templates:** Created via UI, stored in SQLite, accessed via `custom-{uuid}` slug

### Template Versioning Strategy

**For Git-tracked templates (presentation-templates/):**
- Templates are part of the codebase and sync with upstream
- NH-specific templates should be in `nh-*` directories to avoid conflicts
- During upstream sync, preserve NH directories

**For Database templates (app_data/fastapi.db):**
- Not version controlled - back up separately
- Export templates before major updates
- Can be migrated via SQL or re-created from source PPTX

### Backing Up Custom Templates

```bash
# Backup database templates
cp app_data/fastapi.db app_data/fastapi.db.backup

# Export specific template (if export endpoint exists)
# Or manually backup the presentation-templates directory
tar -czf nh-templates-backup.tar.gz servers/nextjs/presentation-templates/nh-*
```

### Restoring After Upstream Sync

If NH templates are lost during sync:
1. Check `git stash list` for stashed changes
2. Restore from backup: `git checkout nh-custom -- servers/nextjs/presentation-templates/nh-*`
3. For database templates, restore `app_data/fastapi.db` from backup

### Making Changes
1. Always work on the `nh-custom` branch
2. Commit changes with descriptive messages
3. Push to origin: `git push origin nh-custom`
4. Periodically sync with upstream using `/sync-upstream`
