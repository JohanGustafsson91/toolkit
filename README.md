# Developer Toolkit

A collection of reusable development components including GitHub Actions workflows, templates, and coding standards for consistent development practices across projects.

## Contents

This toolkit contains:
- **GitHub Actions Workflows**: Reusable CI/CD workflows for consistent automation
- **Dependabot Templates**: Standardized dependency management configurations
- **Development Standards**: (Coming soon) Coding guidelines and best practices

## Available Workflows

### 1. Validate Workflow (`validate.yml`)

Runs linting, testing, and building steps for your project. Supports npm, pnpm, and yarn.

#### Usage

Create a workflow file in your repository (e.g., `.github/workflows/ci.yml`):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
     uses: YOUR_USERNAME/toolkit/.github/workflows/validate.yml@main
    with:
      node-version: '20.x'
      package-manager: 'pnpm'
      lint-script: 'lint'
      test-script: 'test'
      build-script: 'build'
```

#### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `node-version` | Node.js version to use | No | `20.x` |
| `package-manager` | Package manager (npm, pnpm, or yarn) | No | `npm` |
| `lint-script` | npm script for linting | No | `lint` |
| `test-script` | npm script for testing | No | `test` |
| `build-script` | npm script for building | No | `build` |
| `skip-lint` | Skip linting step | No | `false` |
| `skip-test` | Skip testing step | No | `false` |
| `skip-build` | Skip build step | No | `false` |

### 2. Auto-merge Dependabot (`auto-merge-dependabot.yml`)

Automatically merges Dependabot PRs after all checks pass.

#### Usage

Create a workflow file in your repository (e.g., `.github/workflows/auto-merge-dependabot.yml`):

```yaml
name: Auto-merge Dependabot

on:
  pull_request:

jobs:
  auto-merge:
     uses: YOUR_USERNAME/toolkit/.github/workflows/auto-merge-dependabot.yml@main
    with:
      merge-method: 'squash'
      exclude: 'major'
```

#### Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `merge-method` | Merge method (squash, merge, rebase) | No | `squash` |
| `exclude` | Exclude major, minor, or patch updates | No | `major` |

### 3. Dependabot Configuration Templates

Dependabot configuration files must exist in each repository (they cannot be referenced externally like workflows). This repository provides templates and a sync script to make it easy to maintain consistent Dependabot configurations across all your repositories.

#### Available Templates

- **`dependabot-npm.yml`** - For Node.js/npm projects with smart grouping and auto-merge settings
- **`dependabot-github-actions.yml`** - For monitoring GitHub Actions versions

#### Sync Script Usage

Use the provided `sync-dependabot.sh` script to copy a template to your repository:

```bash
# Sync npm template (default)
./sync-dependabot.sh ~/code/my-repo

# Sync npm template (explicit)
./sync-dependabot.sh ~/code/my-repo npm

# Sync GitHub Actions template
./sync-dependabot.sh ~/code/my-repo github-actions
```

The script will:
- Create a backup of any existing `dependabot.yml` file
- Copy the selected template to `.github/dependabot.yml`
- Provide next steps for committing the changes

#### Manual Installation

If you prefer to copy manually:

1. Browse the `templates/` directory
2. Copy your desired template to your repository's `.github/dependabot.yml`
3. Customize as needed for your project

## Installation in Your Repository

### Option 1: Reference Workflows Directly (Recommended)

Simply reference the workflows in your repository as shown in the usage examples above. No package installation needed.

### Option 2: Use the Sync Script for Dependabot

Clone this repository and use the sync script:

```bash
git clone https://github.com/YOUR_USERNAME/toolkit.git
cd toolkit
./sync-dependabot.sh ~/path/to/your/repo npm
```

## Complete Example

Here's a complete setup for a repository:

**.github/workflows/ci.yml:**
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  validate:
     uses: YOUR_USERNAME/toolkit/.github/workflows/validate.yml@main
    with:
      node-version: '20.x'
      package-manager: 'pnpm'
```

**.github/workflows/auto-merge-dependabot.yml:**
```yaml
name: Auto-merge Dependabot

on:
  pull_request:

jobs:
  auto-merge:
    needs: [validate] # Wait for CI to pass
     uses: YOUR_USERNAME/toolkit/.github/workflows/auto-merge-dependabot.yml@main
```

**.github/dependabot.yml:**
```yaml
# Copy from this repository's .github/dependabot.yml
```

## Tips

- Pin workflows to a specific version/tag for stability: `@v1.0.0`
- Use `@main` to always get the latest version
- Combine the validate workflow with auto-merge for automated dependency management
- Customize script names based on your package.json scripts

## License

MIT
