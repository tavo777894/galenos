# Historia Clínica Electrónica - MVP SPRINT 1 (DEMO PRO)

Sistema profesional de Historia Clínica Electrónica con arquitectura en capas, auditoría completa y gestión de documentos.

## 🚀 Características Sprint 1

### ✅ Arquitectura Profesional
- **Arquitectura en capas**: Separación clara entre modelos, servicios, esquemas y endpoints
- **Clean Code**: Código limpio, documentado y mantenible
- **Type Safety**: Validación robusta con Pydantic
- **Error Handling**: Manejo profesional de errores y excepciones

### ✅ Autenticación Avanzada
- **JWT Tokens**: Access tokens (30 min) + Refresh tokens (7 días)
- **Roles Multi-nivel**: ADMIN, DOCTOR, SECRETARIA
- **Endpoint /refresh**: Renovación de tokens sin re-autenticación
- **Seguridad**: Hash bcrypt para contraseñas

### ✅ Sistema de Auditoría
- **Registro Automático**: Toda acción importante queda registrada
- **Tabla audit_logs**: user_id, entity, entity_id, action, timestamp, metadata JSON
- **Acciones Auditadas**:
  - CREATE/UPDATE/DELETE de pacientes
  - GENERATE/DOWNLOAD/PRINT de documentos
  - Metadata detallada de cambios

### ✅ Gestión de Pacientes
- **CRUD Completo** con audit logging integrado
- **Campos Extendidos**:
  - Información personal (nombre, CI, fecha nacimiento)
  - Contacto (teléfono, email, dirección)
  - **Contacto de Emergencia** (nombre, teléfono, relación)
  - Información médica (alergias, antecedentes)
- **Búsqueda por CI**
- **Cálculo automático de edad**

### ✅ Motor de Documentos PDF
- **Generación Profesional**: HTML (Jinja2) → PDF (WeasyPrint)
- **Template Personalizable**:
  - Logo de clínica (opcional, configurable)
  - Encabezado con nombre, dirección, teléfono
  - Sección de contacto de emergencia
  - Alert visual para alergias importantes
  - Footer con fecha de generación

- **Almacenamiento Inteligente**:
  - Organización por fecha (YYYY/MM)
  - Hash SHA256 para integridad
  - Verificación de integridad en descarga

### ✅ Historial de Documentos
- **Tabla documents**: Registro completo de PDFs generados
- **Metadata**:
  - tipo, patient_id, created_by, created_at
  - pdf_path, file_hash, file_size, filename
- **Endpoints**:
  - Listar documentos (filtro por paciente/tipo)
  - Descargar PDF guardado
  - Preview inline
  - Reimprimir con audit log

### ✅ Base de Datos
- **PostgreSQL**: Producción (docker-compose)
- **SQLite**: Desarrollo (fallback automático)
- **Alembic**: Migraciones versionadas
- **4 Tablas**: users, patients, documents, audit_logs

## 📋 Estructura del Proyecto

```
galenos/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py          # Login, register, refresh token
│   │   │   ├── patients.py      # CRUD + PDF generation
│   │   │   └── documents.py     # List, download, reprint
│   │   └── router.py
│   ├── core/
│   │   ├── config.py            # Settings + logo/storage paths
│   │   ├── security.py          # JWT (access + refresh)
│   │   └── deps.py              # Auth dependencies
│   ├── db/
│   │   └── session.py
│   ├── models/
│   │   ├── user.py              # User + UserRole (ADMIN/DOCTOR/SECRETARIA)
│   │   ├── patient.py           # Patient + emergency contact
│   │   ├── audit_log.py         # AuditLog
│   │   └── document.py          # Document + DocumentType
│   ├── schemas/
│   │   ├── user.py              # Token, RefreshTokenRequest
│   │   ├── patient.py
│   │   ├── document.py
│   │   └── audit_log.py
│   ├── services/
│   │   ├── pdf_service.py       # PDF generation + hash + storage
│   │   └── audit_service.py     # Audit logging helpers
│   ├── templates/
│   │   └── patient_card.html    # Professional PDF template
│   └── main.py
├── alembic/                     # Database migrations
├── scripts/
│   └── seed_data.py             # 3 users + 5 patients
├── storage/documents/           # PDF storage (auto-created)
├── .env
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README_MVP_SPRINT1.md
```

## 🛠️ Instalación Rápida

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables

Edita `.env`:

```env
CLINIC_NAME=Tu Clínica
CLINIC_ADDRESS=Tu dirección
CLINIC_PHONE=Tu teléfono
CLINIC_LOGO_PATH=./assets/logo.png  # Opcional

DOCUMENTS_STORAGE_PATH=./storage/documents

# SQLite (desarrollo)
DATABASE_URL=sqlite:///./galenos.db

# O PostgreSQL (producción)
# DATABASE_URL=postgresql://user:pass@localhost:5432/galenos_db
```

### 3. Iniciar PostgreSQL (Opcional)

```bash
docker-compose up -d
```

### 4. Crear Base de Datos

```bash
# Generar migración inicial
alembic revision --autogenerate -m "Initial migration with audit and documents"

# Aplicar migración
alembic upgrade head

# Cargar datos de prueba
python scripts/seed_data.py
```

### 5. Ejecutar Aplicación

```bash
python run.py
```

Visita: http://localhost:8000/docs

## 🔐 Credenciales de Prueba

| Rol | Username | Password | Permisos |
|-----|----------|----------|----------|
| ADMIN | admin | admin123 | Acceso completo |
| DOCTOR | doctor | doctor123 | Acceso completo |
| SECRETARIA | secretaria | secretaria123 | Acceso completo |

## 📡 API Endpoints

### Autenticación

```
POST   /api/v1/auth/login         # Login → access_token + refresh_token
POST   /api/v1/auth/refresh       # Refresh access_token
POST   /api/v1/auth/register      # Crear usuario
```

### Pacientes

```
POST   /api/v1/patients/                    # Crear paciente
GET    /api/v1/patients/                    # Listar pacientes
GET    /api/v1/patients/{id}                # Ver paciente
PUT    /api/v1/patients/{id}                # Actualizar paciente
DELETE /api/v1/patients/{id}                # Eliminar paciente
GET    /api/v1/patients/search/ci/{ci}      # Buscar por CI

# PDF Generation
POST   /api/v1/patients/{id}/generate-card  # Generar y guardar PDF
GET    /api/v1/patients/{id}/card-pdf       # Preview rápido (no guarda)
```

### Documentos

```
GET    /api/v1/documents/                   # Listar documentos
GET    /api/v1/documents/{id}               # Metadata de documento
GET    /api/v1/documents/{id}/download      # Descargar PDF
GET    /api/v1/documents/{id}/preview       # Preview inline
POST   /api/v1/documents/{id}/reprint       # Reimprimir (con audit)
DELETE /api/v1/documents/{id}               # Eliminar registro
```

## 🔄 Flujo de Trabajo Típico

### 1. Autenticación

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=doctor&password=doctor123"

# Respuesta:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}

# Usar el access_token en headers:
Authorization: Bearer eyJ...
```

### 2. Crear Paciente

```bash
curl -X POST "http://localhost:8000/api/v1/patients/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "Pérez",
    "ci": "12345678",
    "date_of_birth": "1985-06-15",
    "phone": "+591 70123456",
    "address": "Calle Principal 123",
    "emergency_contact_name": "María Pérez",
    "emergency_contact_phone": "+591 70123457",
    "emergency_contact_relationship": "Esposa",
    "allergies": "Penicilina",
    "medical_history": "Hipertensión controlada"
  }'
```

### 3. Generar Ficha PDF

```bash
# Generar y guardar
curl -X POST "http://localhost:8000/api/v1/patients/1/generate-card" \
  -H "Authorization: Bearer TOKEN"

# Respuesta:
{
  "document_id": 1,
  "filename": "ficha_paciente_12345678_20260105_143022.pdf",
  "created_at": "2026-01-05T14:30:22",
  "download_url": "/api/v1/documents/1/download"
}
```

### 4. Descargar PDF

```bash
curl -X GET "http://localhost:8000/api/v1/documents/1/download" \
  -H "Authorization: Bearer TOKEN" \
  --output ficha.pdf
```

## 🎨 Personalización

### Logo de Clínica

1. Guarda tu logo en `./assets/logo.png`
2. Actualiza `.env`:
   ```
   CLINIC_LOGO_PATH=./assets/logo.png
   ```

El logo aparecerá automáticamente en el PDF (max 120x80px).

### Template PDF

Edita `app/templates/patient_card.html` para personalizar:
- Colores y estilos
- Secciones adicionales
- Layout

## 📊 Sistema de Auditoría

Todas las acciones quedan registradas en `audit_logs`:

```sql
SELECT
  al.created_at,
  u.username,
  al.action,
  al.entity,
  al.description,
  al.metadata
FROM audit_logs al
JOIN users u ON al.user_id = u.id
ORDER BY al.created_at DESC;
```

Acciones auditadas:
- `patient.create` - Creación de paciente
- `patient.update` - Actualización (con campos cambiados en metadata)
- `patient.delete` - Eliminación
- `document.generate` - Generación de PDF
- `document.download` - Descarga
- `document.print` - Impresión/reimpresión

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ JWT con expiración (access: 30min, refresh: 7 días)
- ✅ Validación de integridad de PDFs (SHA256)
- ✅ CORS configurableREQUIEREN autenticación
- ✅ Roles y permisos (preparado para futuras restricciones)

## 🚦 Testing

```bash
# Acceder a Swagger UI
http://localhost:8000/docs

# Usar botón "Authorize" con el access_token
# Probar todos los endpoints interactivamente
```

## 📦 Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history
```

## 🐳 Docker (PostgreSQL)

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f postgres

# Detener
docker-compose down

# Eliminar datos
docker-compose down -v
```

## 📈 Próximos Sprints

**Sprint 2** (Sugerencias):
- Consultas médicas
- Recetas médicas
- Dashboard con estadísticas
- Búsqueda avanzada
- Roles con permisos granulares
- Endpoints de auditoría
- Exportación de reportes

**Sprint 3**:
- Sistema de citas
- Notificaciones
- Historias clínicas completas
- Laboratorios e imágenes
- Facturación

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push (`git push origin feature/nueva-funcionalidad`)
5. Pull Request

## 📝 Licencia

Proyecto privado y confidencial.

---

**Desarrollado con FastAPI, PostgreSQL y Python**
*Sprint 1 - MVP Profesional Demo*
