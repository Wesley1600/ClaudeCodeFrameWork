# Build Automation Skill

Automates build, test, and deployment processes using Bash scripts without loading build logic into context.

## Description

This skill provides a complete CI/CD pipeline using Bash scripts. It handles building, testing, and deploying applications with proper error handling and reporting.

## When to Use

Use this skill when:
- User wants to build the project
- User requests running tests
- User wants to deploy the application
- User needs to set up a development environment

## Usage

### Full Pipeline

Execute the complete pipeline:

```bash
bash .claude/skills/build-automation/scripts/bash/pipeline.sh
```

This runs: build → test → deploy (if tests pass)

### Individual Steps

**Build only:**
```bash
bash .claude/skills/build-automation/scripts/bash/build.sh
```

**Test only:**
```bash
bash .claude/skills/build-automation/scripts/bash/test.sh
```

**Deploy only:**
```bash
bash .claude/skills/build-automation/scripts/bash/deploy.sh
```

**Setup environment:**
```bash
bash .claude/skills/build-automation/scripts/bash/setup.sh
```

**Clean artifacts:**
```bash
bash .claude/skills/build-automation/scripts/bash/cleanup.sh
```

## Script Reference

### pipeline.sh

Executes the complete build pipeline with proper error handling.

**Exit Codes:**
- 0: Pipeline completed successfully
- 1: Build failed
- 2: Tests failed
- 3: Deployment failed

**Output:** Progress messages and final status

### build.sh

Compiles the project and generates build artifacts.

**Exit Codes:**
- 0: Build successful
- 1: Build failed

**Artifacts:** Creates `build/` directory with compiled files

### test.sh

Runs the test suite and generates reports.

**Exit Codes:**
- 0: All tests passed
- 1: Tests failed

**Output:** Test results and coverage report

### deploy.sh

Deploys the application (mock deployment in this example).

**Environment Variables:**
- `DEPLOY_ENV`: Target environment (dev|staging|prod, default: dev)
- `DEPLOY_DRY_RUN`: If set, runs in dry-run mode

**Exit Codes:**
- 0: Deployment successful
- 1: Deployment failed

### setup.sh

Sets up the development environment.

**Actions:**
- Creates necessary directories
- Checks dependencies
- Initializes configuration

### cleanup.sh

Removes build artifacts and temporary files.

**Actions:**
- Removes `build/` directory
- Removes temporary files
- Cleans caches

## Environment Configuration

Scripts use configuration from `scripts/shared/config.env`:

```bash
# Load configuration
source scripts/shared/config.env
```

## Error Handling

All scripts:
- Exit on first error (set -e)
- Report clear error messages
- Return appropriate exit codes
- Log to both stdout and stderr

## Examples

**Example 1: Full build and deploy**
```bash
bash scripts/bash/pipeline.sh
```

**Example 2: Build for specific environment**
```bash
DEPLOY_ENV=production bash scripts/bash/pipeline.sh
```

**Example 3: Test in dry-run mode**
```bash
DEPLOY_DRY_RUN=1 bash scripts/bash/deploy.sh
```

**Example 4: Clean and rebuild**
```bash
bash scripts/bash/cleanup.sh && bash scripts/bash/build.sh
```

## Dependencies

- Bash 4.0+
- Standard Unix utilities (grep, sed, awk)
- Project-specific build tools (configured in setup.sh)

## Security

- Scripts validate environment variables
- Dry-run mode for safe testing
- No destructive operations without confirmation
