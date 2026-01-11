# Índice Mgrep - Mejoras SportsClub

## Términos de Búsqueda para Mgrep

### CI/CD Security Tools
- bandit safety pip-audit trufflehog gitleaks semgrep
- security scan vulnerability dependency check
- JSON reports artifacts upload GitHub Actions
- Ruff linter formatter check Python linting

### API Authentication
- ApiKey model Django authentication X-API-Key header
- Bearer token Django Ninja authentication class
- API key generation management command
- user foreign key expires_at is_active valid

### Dependencies Management
- requirements.txt version pinning explicit dependencies
- 12-factor app reproducible builds security
- Django==6.0.1 django-ninja==1.5.2 psycopg==3.3.2

### Django Admin
- ApiKeyAdmin admin interface list display
- readonly fields search filters API key management

### Error Handling
- exception chaining raise from err Ruff B904
- CommandError user does not exist generate_api_key

### Blue/Green Deployment
- docker-compose nginx load balancer
- app-blue app-green health check reverse proxy

## Archivos Clave Modificados

### .github/workflows/ci.yml
- Security tools installation and scanning
- JSON report generation with fallback
- Test environment with DEBUG=True

### requirements.txt
- Explicit version pinning for all dependencies
- 12-factor app methodology documentation

### core/models/api_key.py
- ApiKey model with user relationship
- expiration tracking and validation methods

### core/auth.py
- ApiKeyAuth and ApiKeyHeaderAuth classes
- DEBUG mode authentication disabling

### core/admin.py
- ApiKeyAdmin configuration for Django admin

### core/management/commands/generate_api_key.py
- Management command for API key generation
- JSON and text output formats

### sportsclub/api.py
- Django Ninja API authentication configuration

## Commits de Referencia

1. 3f94de3 - Implement security enhancements and API authentication
2. 6444ecc - Fix CI/CD pipeline and authentication for tests
3. 1729a30 - Fix exception chaining in generate_api_key.py

## Conceptos Educativos Implementados

### DevSecOps
- Security scanning in CI/CD pipeline
- Automated vulnerability detection
- Dependency audit and secret scanning

### API Security
- Token-based authentication
- Key expiration and rotation
- Admin interface for management

### Software Engineering Best Practices
- Explicit dependency declaration
- Code linting and formatting
- Error handling and exception chaining
- Configuration as code

## Búsquedas Semánticas Sugeridas

```
mgrep "security tools in CI pipeline"
mgrep "API authentication implementation Django"
mgrep "version pinning dependencies requirements"
mgrep "Django admin interface API keys"
mgrep "management command generate API keys"
mgrep "exception handling best practices"
mgrep "Blue/Green deployment configuration"
```

## Contexto del Proyecto

Proyecto educativo SportsClub para enseñar:
- Despliegue seguro con CI/CD
- Desarrollo frontend con APIs REST
- Metodología 12-factor app
- Blue/Green deployments
- Seguridad integrada (DevSecOps)

Las mejoras implementadas cubren las tres áreas identificadas para aprendizaje:
1. Dependencias explícitas y version pinning
2. Herramientas de seguridad en pipeline CI/CD
3. Autenticación en endpoints API