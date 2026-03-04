# Production Deployment Guide for Proxmox LXC

This guide provides step-by-step instructions for deploying the Sports Club application to a Proxmox LXC server in a production-hardened state.

## Prerequisites

1. **Proxmox LXC Server** with:
   - Docker and Docker Compose installed
   - SSH access configured
   - Port 80 open for HTTP traffic

2. **GitHub Repository** with:
   - Docker Hub credentials stored as secrets (`DOCKER_USERNAME`, `DOCKER_PASSWORD`)
   - CI/CD pipeline configured (`.github/workflows/ci.yml` and `.github/workflows/docker-publish.yml`)

3. **Docker Hub Account** with:
   - Public repository named `sportsclub`
   - Personal Access Token (PAT) generated

## Task 1: Container Hardening - Already Implemented

The Dockerfile (`docker/app/Dockerfile`) already includes container hardening:

1. **Non-privileged user**: Creates `appuser` user (lines 29-30)
2. **File ownership**: Changes ownership of `/app` to `appuser` (line 32)
3. **User switching**: Runs application as `appuser` (line 35)

Verification command:
```bash
docker exec <container_name> whoami
# Should return: appuser
```

## Task 2: Production Configuration

The `docker-compose.production.yml` file provides production overrides:

### Key Security Features:
1. **Restart policies**: `unless-stopped` for all services
2. **Port security**:
   - PostgreSQL ports removed (internal only)
   - NGINX exposes only port 80
3. **DEBUG mode**: Set to `False` for production
4. **Network isolation**: Database only accessible internally

## Task 3: Secrets Management

### Creating Production Secrets

1. **Generate strong secrets** on your local machine:
```bash
# Generate Django secret key
openssl rand -base64 64

# Generate PostgreSQL password
openssl rand -base64 32
```

2. **Create `.env.production` file** (NEVER commit to git):
```bash
cp .env.production.example .env.production
# Edit with actual values
```

3. **Secure transfer to Proxmox LXC**:
```bash
# Method 1: SCP (Secure Copy)
scp .env.production user@proxmox-server:/opt/sportsclub/

# Method 2: SSH and manual creation
ssh user@proxmox-server
nano /opt/sportsclub/.env.production
# Paste contents manually
```

### Security Considerations:
- Use SSH keys for authentication (disable password auth)
- Transfer over VPN or encrypted tunnel
- Set strict file permissions: `chmod 600 .env.production`
- Rotate secrets regularly

## Task 4: Deployment and Verification

### Step 1: Connect to Proxmox LXC
```bash
ssh user@proxmox-server-ip
```

### Step 2: Clone/Pull Repository
```bash
cd /opt
git clone https://github.com/your-username/sportsclub.git
cd sportsclub
# Or if already cloned:
git pull origin main
```

### Step 3: Set Up Production Environment
```bash
# Create .env.production file (transferred securely)
# Ensure it has proper permissions
chmod 600 .env.production

# Load environment variables
set -a && source .env.production && set +a
```

### Step 4: Deploy Application
```bash
# Using Docker Compose override pattern
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d --build
```

### Step 5: Verification Tests

1. **Check container status**:
```bash
docker ps
# Should show: postgres, app-blue, app-green, nginx
```

2. **Verify non-root execution**:
```bash
docker exec sportsclub-app-blue-1 whoami
# Should return: appuser
```

3. **Test API access**:
```bash
curl http://localhost/api/v1/openapi.json
# Should return OpenAPI specification
```

4. **Verify DEBUG is False**:
```bash
# Access a non-existent endpoint
curl -I http://localhost/nonexistent
# Should return 404 without debug information
```

5. **Verify database isolation**:
```bash
# From your laptop, try to connect to PostgreSQL
nc -zv proxmox-server-ip 5432
# Should fail (connection refused/timeout)
```

## Task 5: Automated Build and Push Pipeline

### Docker Hub Setup
1. Create repository: `sportsclub` (public)
2. Generate Personal Access Token (PAT)
3. Add GitHub secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub PAT

### GitHub Actions Workflow
The `.github/workflows/docker-publish.yml` file:
- Triggers after successful CI tests
- Builds and pushes image to Docker Hub
- Uses multi-platform build support
- Implements caching for performance

### Production Update
Modify `docker-compose.production.yml` to use Docker Hub image:
```yaml
app-blue:
  image: ${DOCKER_USERNAME}/sportsclub:${APP_VERSION:-latest}
  # Instead of: build: ...
```

### Verification on Proxmox LXC
```bash
# Remove local image
docker rmi $(docker images -q sportsclub-app)

# Pull from Docker Hub
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d
# Should download image from Docker Hub
```

## Security Hardening Summary

### Container Security
- ✅ Non-privileged user execution
- ✅ Minimal base image (python:3.13-slim)
- ✅ No unnecessary packages installed
- ✅ Proper file permissions

### Network Security
- ✅ Database isolated internally
- ✅ Only NGINX exposed (port 80)
- ✅ Internal Docker network
- ✅ Health checks for resilience

### Secrets Management
- ✅ Environment variables for configuration
- ✅ .env.production excluded from git
- ✅ Strong, random secret generation
- ✅ Secure transfer methods

### Deployment Security
- ✅ Blue-green deployment pattern
- ✅ Automated CI/CD pipeline
- ✅ Image signing verification
- ✅ Rollback capability

## Troubleshooting

### Common Issues

1. **Database connection failures**:
```bash
# Check PostgreSQL logs
docker logs sportsclub-postgres-1

# Verify environment variables
echo $POSTGRES_PASSWORD
```

2. **Permission errors**:
```bash
# Check container user
docker exec sportsclub-app-blue-1 whoami

# Verify file ownership in container
docker exec sportsclub-app-blue-1 ls -la /app
```

3. **Port conflicts**:
```bash
# Check what's using port 80
sudo netstat -tulpn | grep :80

# Stop conflicting service or change NGINX port
```

4. **Docker Hub authentication**:
```bash
# Test Docker Hub login
echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin

# Verify image pull
docker pull $DOCKER_USERNAME/sportsclub:latest
```

### Monitoring Commands
```bash
# View logs
docker compose -f docker-compose.yml -f docker-compose.production.yml logs -f

# Resource usage
docker stats

# Health status
docker compose -f docker-compose.yml -f docker-compose.production.yml ps
```

## Maintenance

### Regular Tasks
1. **Update dependencies**: Monthly security updates
2. **Rotate secrets**: Quarterly password rotation
3. **Backup database**: Daily automated backups
4. **Monitor logs**: Real-time log aggregation
5. **Security scanning**: Weekly vulnerability scans

### Backup Procedures
```bash
# Database backup
docker exec sportsclub-postgres-1 pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Volume backup
docker run --rm -v sportsclub_postgres:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

This deployment guide ensures a secure, production-ready deployment of the Sports Club application following industry best practices for container security and DevOps workflows.