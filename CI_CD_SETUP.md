# CI/CD Pipeline Setup

This document describes the enhanced CI/CD pipeline for the OWLban Earnings Dashboard project.

## Overview

The CI/CD pipeline consists of two GitHub Actions workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`): Runs on every push and pull request to main/master branches
2. **CD Workflow** (`.github/workflows/cd.yml`): Runs on every push to main/master branches for automated deployment

## CI Workflow Features

- **Automated Testing**: Runs Jest test suite
- **Linting**: Code quality checks using ESLint
- **Security Audit**: NPM security vulnerability scanning
- **Dependency Caching**: Faster builds with npm cache
- **Node.js 18**: Consistent runtime environment

## CD Workflow Features

- **Docker Image Building**: Automated Docker image creation
- **Container Registry**: Push to Docker Hub
- **Automated Deployment**: SSH-based deployment to production server
- **Rollback Support**: Uses existing deployment scripts

## Required Secrets

Configure the following secrets in your GitHub repository settings:

### Docker Hub Credentials
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password or access token

### Deployment Server Credentials
- `DEPLOY_USER`: SSH username for deployment server
- `DEPLOY_HOST`: IP address or hostname of deployment server

## Setup Instructions

1. **Configure GitHub Secrets**:
   - Go to your repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add the required secrets listed above

2. **Update Deployment Path**:
   - In `.github/workflows/cd.yml`, replace `/path/to/deployment/directory` with the actual path on your server where the project is deployed

3. **Server Setup**:
   - Ensure Docker is installed on your deployment server
   - Ensure PM2 is installed globally (`npm install -g pm2`)
   - Copy your deployment scripts (`deploy.sh`) to the server
   - Set up SSH key authentication for GitHub Actions

## Workflow Triggers

### CI Workflow
- Triggers on pushes to `main` or `master` branches
- Triggers on pull requests to `main` or `master` branches

### CD Workflow
- Triggers only on pushes to `main` or `master` branches
- Does not run on pull requests to prevent accidental deployments

## Local Development

The CI/CD setup includes linting. To run linting locally:

```bash
cd OSCAR-BROOME-REVENUE
npm install
npm run lint
npm run lint:fix  # To auto-fix linting issues
```

## Monitoring and Troubleshooting

- Check GitHub Actions tab in your repository for workflow runs
- View logs for each step to identify issues
- Use `continue-on-error: true` for non-blocking steps like linting and security audits

## Security Considerations

- Secrets are encrypted and only accessible to the workflow
- SSH connections use strict host key checking disabled for automation
- Docker images are built from source for transparency
- Security audits run on every CI build

## Future Enhancements

Potential improvements to consider:
- Multi-stage Docker builds for smaller images
- Blue-green deployment strategy
- Integration with monitoring tools
- Automated rollback on deployment failures
- Environment-specific configurations (staging/production)
