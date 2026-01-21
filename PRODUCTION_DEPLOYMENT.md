# Production Deployment Guide

This document outlines the secure production deployment configuration for the Sports Club Django application using Docker Compose override patterns. All changes follow security best practices and enable automated CI/CD pipelines.

## Summary of Changes

### 1. Container Hardening (Dockerfile)
**File:** `docker/app/Dockerfile`
- Added non-privileged user `appuser` for security
- Changed ownership of `/app` directory to `appuser`
- Switched to non-privileged user with `USER appuser`
- Removed unnecessary root privileges

### 2. Production Configuration Override
**File:** `docker-compose.production.yml`
- Removes PostgreSQL port exposure to external network
- Sets `restart: unless-stopped` policies for all services
- Configures production environment variables (`DEBUG=False`, proper `ALLOWED_HOSTS`)
- Adjusts healthcheck intervals for production reliability
- Uses Docker Hub images instead of local builds
- Implements blue-green deployment with configurable active color

### 3. Secrets Management Template
**File:** `.env.production.example`
- Template for production environment variables
- Instructions for generating strong secrets using OpenSSL
- Includes database credentials, Django secret key, Docker Hub username
- Blue-green deployment configuration variables

### 4. Automated Docker Image Publishing
**File:** `.github/workflows/docker-publish.yml`
- Builds and pushes Docker image to Docker Hub after successful CI
- Triggers on successful completion of the CI workflow on main branch
- Uses metadata extraction for semantic version tagging
- Implements GitHub Actions cache for build optimization
- Security: Uses GitHub token for authentication, excludes secrets from image layers

### 5. Blue-Green Deployment (Bonus)
**Files Modified:**
- `docker/nginx/Dockerfile`: Added envsubst support and `ACTIVE_COLOR` environment variable
- `docker/nginx/nginx.conf.template`: Template with configurable active upstream
- `docker-compose.production.yml`: Added `ACTIVE_COLOR` variable for nginx
- `.env.production.example`: Added `ACTIVE_COLOR` and `APP_VERSION` variables

## Deployment Instructions

### Prerequisites
1. Docker and Docker Compose installed on production server
2. Docker Hub account with repository `username/sportsclub`
3. GitHub repository with configured secrets:
   - `DOCKER_USERNAME`: Docker Hub username
   - `DOCKER_PASSWORD`: Docker Hub password/access token
   - `GITHUB_TOKEN`: Automatically provided by GitHub

### Step 1: Configure Production Environment
1. Copy `.env.production.example` to `.env.production`:
   ```bash
   cp .env.production.example .env.production
   ```
2. Edit `.env.production` with actual values:
   - Generate strong secrets using OpenSSL:
     ```bash
     openssl rand -base64 64  # SECRET_KEY
     openssl rand -base64 32  # POSTGRES_PASSWORD
     ```
   - Set `ALLOWED_HOSTS` to your production domain(s)
   - Set `DOCKER_USERNAME` to your Docker Hub username
   - Configure `ACTIVE_COLOR` (blue or green) for blue-green deployment
   - Set `APP_VERSION` to desired image tag (default: latest)

### Step 2: Deploy to Production Server (Proxmox LXC)
1. Transfer files to production server:
   - `docker-compose.yml`
   - `docker-compose.production.yml`
   - `.env.production`
   - `docker/` directory (optional, for nginx configuration)

2. Log in to Docker Hub on production server:
   ```bash
   echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
   ```

3. Start the production stack:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.production.yml up -d
   ```

4. Verify deployment:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.production.yml ps
   docker compose -f docker-compose.yml -f docker-compose.production.yml logs
   ```

### Step 3: Blue-Green Deployment Switch
To switch the active deployment color:
1. Update `.env.production`:
   ```
   ACTIVE_COLOR=green
   ```
2. Recreate nginx service:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.production.yml up -d --force-recreate nginx
   ```

### Step 4: Update Application Version
To deploy a new version of the application:
1. The CI/CD pipeline automatically builds and pushes new images to Docker Hub
2. Update `.env.production`:
   ```
   APP_VERSION=v1.2.3  # Or use specific tag from Docker Hub
   ```
3. Recreate app services:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.production.yml up -d --force-recreate app-blue app-green
   ```

## Security Features

### Container Security
- Non-privileged user execution
- No root processes in application containers
- PostgreSQL port not exposed externally
- Internal network communication only

### Secrets Management
- Environment variables for sensitive data
- `.env.production` excluded from version control
- Strong password generation guidance
- Docker secrets excluded from image layers

### Network Security
- Only nginx exposed on port 80
- Internal DNS aliases for service discovery
- Database only accessible within Docker network

### CI/CD Security
- Workflow runs only on successful CI
- Uses GitHub-provided tokens
- Docker Hub credentials stored as secrets
- Cache scoped to repository and branch

## Verification

### Health Checks
- Application: `curl http://localhost:8080/api/v1/openapi.json`
- Database: Automatic via Docker Compose healthcheck
- Nginx: `curl http://localhost/health`

### Logs and Monitoring
```bash
# View all service logs
docker compose -f docker-compose.yml -f docker-compose.production.yml logs -f

# View specific service logs
docker compose -f docker-compose.yml -f docker-compose.production.yml logs app-blue

# Check service status
docker compose -f docker-compose.yml -f docker-compose.production.yml ps
```

## Troubleshooting

### Common Issues
1. **Database connection errors**: Verify PostgreSQL credentials in `.env.production`
2. **Image pull errors**: Ensure Docker Hub authentication and image exists
3. **Port conflicts**: Check if port 80 is already in use
4. **Permission errors**: Verify `.env.production` file permissions (600 recommended)

### Debug Mode
For debugging, temporarily set `DEBUG=True` in `.env.production` and recreate services.

## References

- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Docker Compose Override Files](https://docs.docker.com/compose/extends/)
- [GitHub Actions Docker Login](https://github.com/docker/login-action)
- [Blue-Green Deployment Pattern](https://martinfowler.com/bliki/BlueGreenDeployment.html)

---

**Delivery Date:** 2026-01-21
**Project:** Sports Club Django Application
**Author:** Claude Code
**Repository:** https://github.com/jsabater/sportsclub