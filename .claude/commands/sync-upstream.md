# Sync Fork with Upstream

Sync the `nh-custom` branch with the latest changes from the upstream `presenton/presenton` repository.

## Process

Execute the following sync workflow:

### 1. Fetch latest from upstream
```bash
git fetch upstream
```

### 2. Update local main to match upstream
```bash
git checkout main
git merge --ff-only upstream/main
git push origin main
```

### 3. Rebase nh-custom onto updated main
```bash
git checkout nh-custom
git rebase main
```

### 4. Handle conflicts if any
If there are merge conflicts:
- Identify the conflicted files
- Review each conflict carefully, preserving North Highland customizations while incorporating upstream changes
- Use `git add <file>` after resolving each conflict
- Run `git rebase --continue` after all conflicts are resolved

### 5. Push updated nh-custom branch
```bash
git push origin nh-custom --force-with-lease
```

### 6. Report sync status
After completion, report:
- Number of new commits from upstream
- Whether any conflicts were encountered and how they were resolved
- Current commit hash of nh-custom branch

## Important Notes
- Always use `--force-with-lease` (not `--force`) for safety
- The `nh-custom` branch contains North Highland customizations that should be preserved
- If conflicts are complex, ask the user for guidance before resolving
