# Dependabot Configuration Sync Guide

This guide explains how to keep Dependabot configurations in sync across multiple repositories.

## Why Use Templates?

Dependabot configuration files must live in each repository's `.github/dependabot.yml` path - they cannot be referenced from external repositories like reusable workflows can. Using templates ensures consistency across all your projects.

## Quick Start

### 1. Clone this repository (one-time setup)

```bash
git clone https://github.com/YOUR_USERNAME/toolkit.git ~/toolkit
```

### 2. Sync to your repositories

```bash
cd ~/toolkit

# Sync npm template to a repository
./sync-dependabot.sh ~/code/my-repo npm

# Sync GitHub Actions template
./sync-dependabot.sh ~/code/my-actions-repo github-actions
```

### 3. Commit and push

```bash
cd ~/code/my-repo
git add .github/dependabot.yml
git commit -m "chore: sync dependabot config from central template"
git push
```

## Available Templates

### `npm` (Node.js projects)
- Daily dependency updates at 09:00 UTC
- Smart grouping of production and dev dependencies
- Configured for auto-merge with minor/patch updates
- Excludes major version updates from auto-merge

**Best for:** Node.js, React, Vue, Next.js, Express projects

### `github-actions` (Action repositories)
- Weekly updates on Mondays at 09:00 UTC
- Keeps GitHub Actions up to date
- Limits to 5 open PRs

**Best for:** Repositories that use GitHub Actions

## Keeping Configs in Sync

When you update the templates in this repository:

```bash
cd ~/toolkit
git pull  # Get latest template changes

# Re-sync to all your repositories
./sync-dependabot.sh ~/code/project1 npm
./sync-dependabot.sh ~/code/project2 npm
./sync-dependabot.sh ~/code/project3 npm
```

## Script Features

- **Automatic backups**: Creates timestamped backups before overwriting
- **Safety checks**: Validates paths and templates before copying
- **Color output**: Clear visual feedback during execution
- **Error handling**: Provides helpful error messages

## Manual Sync (Alternative)

If you prefer not to use the script:

```bash
cp ~/toolkit/templates/dependabot-npm.yml ~/code/my-repo/.github/dependabot.yml
```

## Customizing Templates

You can customize the templates in this repository to match your team's preferences:

1. Edit `templates/dependabot-npm.yml` or create new templates
2. Commit changes to this repository
3. Re-sync to all your repositories using the script

## Tips

- Run the sync script whenever you update the central templates
- Consider adding the sync script to your onboarding documentation
- Use the same template across similar projects for consistency
- Create custom templates for special project types (e.g., monorepos, Docker projects)
