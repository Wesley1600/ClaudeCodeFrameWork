# Build Automation Skill Example

This example demonstrates how to organize Bash scripts within a Claude Code skill for build automation.

## Structure

```
bash-skill/
├── SKILL.md                    # Skill description (loaded into Claude's context)
├── scripts/
│   ├── bash/
│   │   ├── pipeline.sh        # Complete pipeline orchestration
│   │   ├── build.sh           # Build script
│   │   ├── test.sh            # Test script
│   │   ├── deploy.sh          # Deployment script
│   │   ├── setup.sh           # Environment setup
│   │   └── cleanup.sh         # Cleanup script
│   └── shared/
│       └── config.env         # Shared configuration
└── README.md                   # This file (developer documentation)
```

## Key Features

1. **Modular Pipeline**: Separate scripts for each stage
2. **Error Handling**: Proper exit codes and error messages
3. **Configuration**: Centralized config in `config.env`
4. **Logging**: Colored output with different log levels
5. **Safety**: Dry-run mode and confirmations for destructive operations

## Usage

### Complete Pipeline

Run the entire build → test → deploy pipeline:

```bash
bash scripts/bash/pipeline.sh
```

### Individual Stages

```bash
# Build only
bash scripts/bash/build.sh

# Test only
bash scripts/bash/test.sh

# Deploy only
bash scripts/bash/deploy.sh

# Setup environment
bash scripts/bash/setup.sh

# Clean artifacts
bash scripts/bash/cleanup.sh
```

### With Configuration

```bash
# Deploy to staging
DEPLOY_ENV=staging bash scripts/bash/deploy.sh

# Dry run deployment
DEPLOY_DRY_RUN=1 bash scripts/bash/deploy.sh

# Custom build directory
BUILD_DIR=/tmp/mybuild bash scripts/bash/build.sh
```

## Testing

Test the scripts:

```bash
# 1. Setup environment
bash scripts/bash/setup.sh

# 2. Run build
bash scripts/bash/build.sh

# 3. Run tests
bash scripts/bash/test.sh

# 4. Deploy (dry run)
DEPLOY_DRY_RUN=1 bash scripts/bash/deploy.sh

# 5. Cleanup
bash scripts/bash/cleanup.sh
```

## Configuration

Edit `scripts/shared/config.env` to customize:

```bash
# Build settings
BUILD_DIR="build"
BUILD_TYPE="release"

# Deployment
DEPLOY_ENV="dev"  # dev, staging, prod

# Logging
LOG_LEVEL="info"  # debug, info, warning, error
```

## Integration with Claude Code

When Claude Code loads this skill:

1. Only `SKILL.md` is loaded into context (~2KB)
2. Claude reads the pipeline instructions
3. When user requests deployment, Claude executes:
   ```bash
   bash .claude/skills/build-automation/scripts/bash/pipeline.sh
   ```
4. Scripts run autonomously with proper error handling

## Benefits

- **Context Efficiency**: ~2KB (SKILL.md) vs ~20KB (if scripts were embedded)
- **Maintainability**: Update scripts without changing skill description
- **Reusability**: Scripts work standalone or in Claude Code
- **Safety**: Dry-run modes and confirmations prevent accidents

## Best Practices Demonstrated

1. **Error Handling**: `set -euo pipefail` in all scripts
2. **Color Output**: Easy-to-read colored logs
3. **Exit Codes**: Meaningful codes for different failure types
4. **Configuration**: Environment variables and config files
5. **Validation**: Input validation and dependency checks
6. **Documentation**: Clear usage instructions and examples
7. **Safety**: Confirmations for production deployments

## Advanced Usage

### Custom Pipeline

Create a custom pipeline for specific workflows:

```bash
#!/usr/bin/env bash
# custom-pipeline.sh

# Build for production
BUILD_TYPE=production bash scripts/bash/build.sh

# Run extended tests
TEST_TIMEOUT=600 bash scripts/bash/test.sh

# Deploy to staging first
DEPLOY_ENV=staging bash scripts/bash/deploy.sh

# If staging successful, deploy to production
if [[ $? -eq 0 ]]; then
    DEPLOY_ENV=production bash scripts/bash/deploy.sh
fi
```

### CI/CD Integration

Use in CI/CD pipelines:

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run pipeline
        run: bash scripts/bash/pipeline.sh
        env:
          DEPLOY_ENV: production
```

## Troubleshooting

**Permission denied:**
```bash
chmod +x scripts/bash/*.sh
```

**Build artifacts not found:**
```bash
# Run build first
bash scripts/bash/build.sh
```

**Environment variable not set:**
```bash
# Check configuration
cat scripts/shared/config.env
```
