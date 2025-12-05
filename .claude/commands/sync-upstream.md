# Sync Fork with Upstream

Sync the `nh-custom` branch with the latest changes from the upstream `presenton/presenton` repository.

## Pre-Sync Checklist

Before starting, verify these critical NH assets:

### NH-Specific Files to Preserve
- [ ] `servers/nextjs/presentation-templates/nh-*/` - NH-branded design templates
- [ ] `servers/fastapi/services/vision_llm_service.py` - Multi-provider vision service
- [ ] `servers/fastapi/api/v1/ppt/endpoints/template_providers.py` - Provider availability endpoint
- [ ] `.claude/` - Claude Code configuration

### Backup Runtime Data (not in git)
```bash
# These are gitignored but should be backed up
cp app_data/fastapi.db app_data/fastapi.db.pre-sync-backup
cp app_data/userConfig.json app_data/userConfig.json.pre-sync-backup
```

## Process

Execute the following sync workflow:

### 1. Create backup of NH templates
```bash
git stash push -m "pre-sync-backup" -- servers/nextjs/presentation-templates/nh-*
```

### 2. Fetch latest from upstream
```bash
git fetch upstream
```

### 3. Update local main to match upstream
```bash
git checkout main
git merge --ff-only upstream/main
git push origin main
```

### 4. Rebase nh-custom onto updated main
```bash
git checkout nh-custom
git rebase main
```

### 5. Handle conflicts if any
If there are merge conflicts:
- Identify the conflicted files
- Review each conflict carefully, preserving North Highland customizations while incorporating upstream changes
- **Priority files to preserve NH changes:**
  - `presentation-templates/` - Keep NH-branded templates
  - `services/vision_llm_service.py` - Keep multi-provider support
  - `api/v1/ppt/endpoints/template_providers.py` - Keep provider endpoint
  - `api/v1/ppt/endpoints/slide_to_html.py` - Keep provider parameter support
- Use `git add <file>` after resolving each conflict
- Run `git rebase --continue` after all conflicts are resolved

### 6. Push updated nh-custom branch
```bash
git push origin nh-custom --force-with-lease
```

### 7. Post-Sync Verification
Verify NH customizations are intact:
```bash
# Check NH templates exist
ls servers/nextjs/presentation-templates/nh-* 2>/dev/null || echo "WARNING: NH templates missing!"

# Check custom services exist
ls servers/fastapi/services/vision_llm_service.py || echo "WARNING: Vision service missing!"

# Check template providers endpoint
ls servers/fastapi/api/v1/ppt/endpoints/template_providers.py || echo "WARNING: Template providers endpoint missing!"
```

### 8. Report sync status
After completion, report:
- Number of new commits from upstream
- Whether any conflicts were encountered and how they were resolved
- Current commit hash of nh-custom branch
- Status of NH templates and custom services

## Important Notes
- Always use `--force-with-lease` (not `--force`) for safety
- The `nh-custom` branch contains North Highland customizations that should be preserved
- If conflicts are complex, ask the user for guidance before resolving
- NH templates in `presentation-templates/nh-*/` are critical assets
- Database templates in `app_data/fastapi.db` are NOT version controlled - backup separately
- After sync, test the `/custom-template` page to verify provider selector works
