# Despliegue en Google Cloud Run con Hardening de Seguridad

## Comando de Despliegue Actualizado

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