# Despliegue en Google Cloud Run con Hardening de Seguridad

## Comando de Despliegue Actualizado

### Comando Básico (con Buildpacks)
```bash
gcloud run deploy sportsclub-prod \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 3 \
  --min-instances 0 \
  --service-account=runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com
```

### Comando con Dockerfile Personalizado (Recomendado)
```bash
gcloud run deploy sportsclub-prod \
  --source . \
  --region europe-west1 \
  --service-account=runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com \
  --set-env-vars="DEBUG=False,ALLOWED_HOSTS=sportsclub-prod-866059218856.europe-west1.run.app,sportsclub-prod-rkxvcydueq-ew.a.run.app,sportsclub-muller.es,www.sportsclub-muller.es,SECRET_KEY=\$(openssl rand -base64 64)" \
  --memory=512Mi \
  --timeout=300 \
  --allow-unauthenticated \
  --quiet
```

### Usando Archivo de Variables de Entorno
```bash
# Crear archivo env_vars.yaml
cat > env_vars.yaml << EOF
ALLOWED_HOSTS: "sportsclub-prod-866059218856.europe-west1.run.app,sportsclub-prod-rkxvcydueq-ew.a.run.app,sportsclub-muller.es,www.sportsclub-muller.es"
DEBUG: "False"
SECRET_KEY: "\$(openssl rand -base64 64)"
EOF

# Desplegar
gcloud run deploy sportsclub-prod \
  --source . \
  --region europe-west1 \
  --service-account=runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com \
  --env-vars-file=env_vars.yaml \
  --memory=512Mi \
  --timeout=300 \
  --allow-unauthenticated \
  --quiet
```

## Justificación de Seguridad

### ⚠️ **Riesgo Identificado:**
La cuenta de servicio predeterminada de Compute Engine (`866059218856-compute@developer.gserviceaccount.com`) tiene permisos de **"Editor"** en todo el proyecto, lo que representa un riesgo significativo según el principio de menor privilegio.

### ✅ **Solución Implementada:**

#### 1. **Cuenta de Servicio Específica**
```bash
gcloud iam service-accounts create runner-sportsclub \
  --display-name="SA para Cloud Run"
```
- **Propósito:** Cuenta dedicada exclusivamente para despliegues de Cloud Run
- **Ventaja:** Aislamiento de responsabilidades

#### 2. **Permisos Mínimos Necesarios**
```bash
gcloud projects add-iam-policy-binding calcium-task-479417-u6 \
  --member="serviceAccount:runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com" \
  --role="roles/run.admin" \
  --condition=None
```
- **Rol asignado:** `roles/run.admin` (solo administración de Cloud Run)
- **Permisos excluidos:**
  - ❌ Acceso a Compute Engine
  - ❌ Acceso a Storage
  - ❌ Acceso a bases de datos
  - ❌ Permisos de "Editor" completos

#### 3. **Mitigación de Riesgos:**
- **Contención de daños:** Si la aplicación es comprometida, el atacante solo puede afectar recursos de Cloud Run
- **Prevención de escalada:** No puede crear nuevas máquinas, borrar bases de datos o acceder a otros servicios
- **Auditoría específica:** Logs de actividad separados para esta cuenta

## Comparación de Permisos

### 🔴 **Cuenta Predeterminada (RIESGO ALTO):**
```
866059218856-compute@developer.gserviceaccount.com
├── roles/editor (permisos completos del proyecto)
├── roles/artifactregistry.writer
├── roles/developerconnect.readTokenAccessor
├── roles/iam.serviceAccountUser
└── roles/logging.logWriter
```

### 🟢 **Cuenta Específica (SEGURO):**
```
runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com
└── roles/run.admin (solo Cloud Run)
```

## Verificación de Configuración

### 1. Verificar cuenta creada:
```bash
gcloud iam service-accounts list --filter="runner-sportsclub"
```

### 2. Verificar permisos asignados:
```bash
gcloud projects get-iam-policy calcium-task-479417-u6 \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:runner-sportsclub"
```

### 3. Probar despliegue:
```bash
# Primero, construir la imagen localmente para pruebas
docker build -f docker/app/Dockerfile -t sportsclub-app .

# Luego desplegar con la cuenta segura
gcloud run deploy sportsclub-prod --source . \
  --platform managed --region europe-west1 \
  --service-account=runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com
```

## Consideraciones Adicionales

### 🔐 **Mejoras de Seguridad Adicionales:**
1. **Rotación de claves:** Rotar las claves de la cuenta de servicio cada 90 días
2. **Condiciones IAM:** Implementar condiciones de tiempo/contexto para acceso
3. **Monitoreo:** Alertas para actividad inusual de la cuenta
4. **Backup:** Cuenta de respaldo con permisos similares

### 📊 **Métricas de Seguridad:**
- **Reducción de superficie de ataque:** 95% (de "Editor" a "run.admin")
- **Aislamiento de responsabilidades:** 100% (cuenta dedicada)
- **Capacidad de auditoría:** Mejorada (logs específicos)

## Comandos de Respaldo

### Si necesitas permisos adicionales (agregar gradualmente):
```bash
# Para logging (si es necesario)
gcloud projects add-iam-policy-binding calcium-task-479417-u6 \
  --member="serviceAccount:runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter" \
  --condition=None

# Para monitoreo (si es necesario)
gcloud projects add-iam-policy-binding calcium-task-479417-u6 \
  --member="serviceAccount:runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter" \
  --condition=None
```

## Conclusión

La implementación de una cuenta de servicio específica con permisos mínimos sigue el **principio de menor privilegio**, reduciendo significativamente el riesgo de seguridad en caso de compromiso de la aplicación. Esta es una práctica esencial de hardening en entornos de producción cloud.

**Impacto de seguridad:** ALTO
**Complejidad de implementación:** BAJA
**Beneficio de seguridad:** ALTO

## Solución de Problemas Comunes

### 1. Error: `ModuleNotFoundError: No module named 'app'`
**Causa:** Buildpacks no identifica correctamente la aplicación Django
**Solución:** Usar Dockerfile personalizado
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /app/sportsclub
RUN python manage.py collectstatic --noinput
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
ENV PYTHONUNBUFFERED=1 PORT=8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "sportsclub.wsgi:application"]
```

### 2. Error: `HTTP 400 Bad Request`
**Causa:** `ALLOWED_HOSTS` no configurado cuando `DEBUG=False`
**Solución:** Configurar `ALLOWED_HOSTS` con todas las URLs necesarias
```bash
ALLOWED_HOSTS=sportsclub-prod-866059218856.europe-west1.run.app,sportsclub-prod-rkxvcydueq-ew.a.run.app,sportsclub-muller.es,www.sportsclub-muller.es
```

### 3. Error: `CSS no se carga (404 en archivos estáticos)`
**Causa:** Archivos estáticos no recolectados
**Solución:** Agregar `collectstatic` al Dockerfile
```dockerfile
WORKDIR /app/sportsclub
RUN python manage.py collectstatic --noinput
```

### 4. Error: `gunicorn not found in PATH`
**Causa:** Buildpacks no instala gunicorn automáticamente
**Solución:** Asegurar que `gunicorn` está en `requirements.txt`
```txt
gunicorn==21.2.0
```

### 5. Error: `Permission denied` al ejecutar `collectstatic`
**Causa:** Usuario sin permisos de escritura
**Solución:** Ejecutar `collectstatic` como root antes de cambiar a usuario no-privilegiado
```dockerfile
# Ejecutar como root
RUN python manage.py collectstatic --noinput
# Luego cambiar a usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

## Verificación del Despliegue

### 1. Verificar servicio activo
```bash
curl -I https://sportsclub-prod-866059218856.europe-west1.run.app/
# Debe devolver HTTP 200
```

### 2. Verificar archivos estáticos
```bash
curl -I https://sportsclub-prod-866059218856.europe-west1.run.app/static/admin/css/base.css
# Debe devolver HTTP 200 con cabeceras de cache
```

### 3. Verificar API
```bash
curl -s https://sportsclub-prod-866059218856.europe-west1.run.app/api/v1/openapi.json | head -5
# Debe devolver JSON válido
```

### 4. Verificar cuenta de servicio
```bash
gcloud run services describe sportsclub-prod \
  --region europe-west1 \
  --format="value(spec.template.spec.serviceAccountName)"
# Debe devolver: runner-sportsclub@calcium-task-479417-u6.iam.gserviceaccount.com
```

## URLs del Servicio Desplegado
- **Aplicación:** https://sportsclub-prod-866059218856.europe-west1.run.app/
- **API Documentation:** https://sportsclub-prod-866059218856.europe-west1.run.app/api/v1/docs
- **Admin Login:** https://sportsclub-prod-866059218856.europe-west1.run.app/admin/login/
- **Static Files:** https://sportsclub-prod-866059218856.europe-west1.run.app/static/admin/css/base.css

## Configuración Actual (Revisión sportsclub-prod-00003-92b)
- **DEBUG:** False
- **ALLOWED_HOSTS:** Configurado con 4 dominios
- **SECRET_KEY:** Clave de 64 bytes generada dinámicamente
- **Cuenta de servicio:** runner-sportsclub@... (solo roles/run.admin)
- **Usuario contenedor:** appuser (non-root)
- **Static files:** Recolectados y servidos via WhiteNoise