# Sprint 3: Consultas Clínicas (SOAP) con Templates y Snippets

## Descripción General

Sprint 3 implementa el módulo completo de consultas clínicas utilizando el formato SOAP (Subjective, Objective, Assessment, Plan), junto con un sistema de plantillas y snippets reutilizables para agilizar la documentación clínica.

## Nuevas Funcionalidades

### 1. Consultas Clínicas (Encounters)

Sistema completo de registro de consultas médicas usando formato SOAP:

- **S (Subjective)**: Motivo de consulta y síntomas del paciente
- **O (Objective)**: Signos vitales y hallazgos del examen físico
- **A (Assessment)**: Diagnóstico o impresión clínica
- **P (Plan)**: Plan de tratamiento y seguimiento

#### Estados de Consulta

- `DRAFT`: Borrador inicial
- `IN_PROGRESS`: Consulta en progreso
- `COMPLETED`: Consulta finalizada
- `CANCELLED`: Consulta cancelada

#### Especialidades Médicas

- General Medicine
- Pediatrics
- Traumatology
- Cardiology
- Dermatology
- Gynecology
- Neurology
- Psychiatry
- Other

### 2. Templates (Plantillas SOAP)

Plantillas predefinidas para diferentes especialidades médicas con contenido por defecto para cada sección SOAP.

**Características:**
- Filtrado por especialidad médica
- Sistema de favoritos por usuario
- Templates activos/inactivos
- Contenido por defecto editable

### 3. Snippets (Fragmentos de Texto)

Fragmentos de texto reutilizables para uso común en consultas.

**Categorías:**
- `diagnosis`: Diagnósticos frecuentes
- `treatment`: Tratamientos estándar
- `prescription`: Recetas comunes
- `recommendation`: Recomendaciones
- `examination`: Hallazgos de examen físico
- `vital_signs`: Signos vitales
- `symptoms`: Síntomas comunes
- `other`: Otros

**Características:**
- Contador de uso (tracking de popularidad)
- Sistema de favoritos por usuario
- Ordenamiento por uso frecuente
- Snippets activos/inactivos

### 4. Sistema de Favoritos

Cada usuario puede marcar templates y snippets como favoritos para acceso rápido.

## API Endpoints

### Encounters (Consultas)

#### POST `/api/v1/encounters/`
Crear nueva consulta

**Roles permitidos:** DOCTOR, ADMIN

**Request:**
```json
{
  "patient_id": 1,
  "specialty": "GENERAL",
  "subjective": "Paciente refiere dolor de cabeza desde hace 3 días...",
  "objective": "PA: 120/80, FC: 72, T°: 36.5°C...",
  "assessment": "Cefalea tensional",
  "plan": "Paracetamol 500mg c/8hrs...",
  "status": "DRAFT"
}
```

**Response:** Encounter creado con auditoría

#### GET `/api/v1/encounters/`
Listar consultas

**Query Params:**
- `patient_id` (optional): Filtrar por paciente
- `skip`: Paginación (default: 0)
- `limit`: Límite (default: 100)

**Roles permitidos:** Todos los autenticados

#### GET `/api/v1/encounters/{encounter_id}`
Ver detalles de consulta

**Response incluye:**
- Datos de la consulta
- Nombre del paciente
- Nombre del doctor

#### PUT `/api/v1/encounters/{encounter_id}`
Actualizar consulta

**Roles permitidos:** DOCTOR, ADMIN

#### PATCH `/api/v1/encounters/{encounter_id}/status`
Actualizar solo el estado

**Roles permitidos:** DOCTOR, ADMIN

**Request:**
```json
{
  "new_status": "COMPLETED"
}
```

#### DELETE `/api/v1/encounters/{encounter_id}`
Eliminar consulta (soft delete → status = CANCELLED)

**Roles permitidos:** DOCTOR, ADMIN

### Templates (Plantillas)

#### POST `/api/v1/templates/`
Crear template

**Roles permitidos:** DOCTOR, ADMIN

**Request:**
```json
{
  "title": "Consulta Pediátrica - Rutina",
  "description": "Template para consultas pediátricas de rutina",
  "specialty": "PEDIATRICS",
  "default_subjective": "Motivo de consulta:\n...",
  "default_objective": "Signos vitales:\n...",
  "default_assessment": "Diagnóstico:\n...",
  "default_plan": "Plan:\n...",
  "is_active": 1
}
```

#### GET `/api/v1/templates/`
Listar templates

**Query Params:**
- `specialty` (optional): Filtrar por especialidad
- `only_active`: Solo activos (default: true)
- `only_favorites`: Solo favoritos del usuario (default: false)
- `skip`, `limit`: Paginación

**Response incluye `is_favorite` flag para cada template**

#### GET `/api/v1/templates/{template_id}`
Ver template específico

#### PUT `/api/v1/templates/{template_id}`
Actualizar template

**Roles permitidos:** DOCTOR, ADMIN

#### DELETE `/api/v1/templates/{template_id}`
Eliminar template (soft delete → is_active = 0)

**Roles permitidos:** DOCTOR, ADMIN

#### POST `/api/v1/templates/{template_id}/favorite`
Agregar template a favoritos

**Roles permitidos:** Todos los autenticados

#### DELETE `/api/v1/templates/{template_id}/favorite`
Remover template de favoritos

**Roles permitidos:** Todos los autenticados

### Snippets (Fragmentos)

#### POST `/api/v1/snippets/`
Crear snippet

**Roles permitidos:** DOCTOR, ADMIN

**Request:**
```json
{
  "title": "Hipertensión Arterial",
  "category": "diagnosis",
  "content": "Hipertensión arterial esencial (CIE-10: I10)...",
  "is_active": 1
}
```

#### GET `/api/v1/snippets/`
Listar snippets

**Query Params:**
- `category` (optional): Filtrar por categoría
- `only_active`: Solo activos (default: true)
- `only_favorites`: Solo favoritos del usuario (default: false)
- `skip`, `limit`: Paginación

**Ordenamiento:** Por uso frecuente (usage_count DESC), luego por título

**Response incluye `is_favorite` flag para cada snippet**

#### GET `/api/v1/snippets/{snippet_id}`
Ver snippet específico

**Nota:** Incrementa automáticamente el contador de uso

#### PUT `/api/v1/snippets/{snippet_id}`
Actualizar snippet

**Roles permitidos:** DOCTOR, ADMIN

#### DELETE `/api/v1/snippets/{snippet_id}`
Eliminar snippet (soft delete → is_active = 0)

**Roles permitidos:** DOCTOR, ADMIN

#### POST `/api/v1/snippets/{snippet_id}/favorite`
Agregar snippet a favoritos

#### DELETE `/api/v1/snippets/{snippet_id}/favorite`
Remover snippet de favoritos

## Base de Datos

### Nuevas Tablas

#### `encounters`
- `id`: Primary key
- `patient_id`: Foreign key → patients
- `doctor_id`: Foreign key → users
- `subjective`: Text (S del SOAP)
- `objective`: Text (O del SOAP)
- `assessment`: Text (A del SOAP)
- `plan`: Text (P del SOAP)
- `specialty`: Enum (MedicalSpecialty)
- `status`: Enum (EncounterStatus)
- `created_at`, `updated_at`: Timestamps

**Índices:**
- `patient_id`
- `doctor_id`
- `created_at`

#### `templates`
- `id`: Primary key
- `title`: String(255)
- `description`: Text
- `specialty`: Enum (MedicalSpecialty)
- `default_subjective`, `default_objective`, `default_assessment`, `default_plan`: Text
- `is_active`: Integer (0/1)
- `created_at`, `updated_at`: Timestamps

**Índice:**
- `specialty`

#### `snippets`
- `id`: Primary key
- `title`: String(255)
- `category`: String(50)
- `content`: Text
- `is_active`: Integer (0/1)
- `usage_count`: Integer (default: 0)
- `created_at`, `updated_at`: Timestamps

**Índice:**
- `category`

#### `user_favorite_templates`
Tabla de asociación many-to-many
- `user_id`: Foreign key → users (CASCADE)
- `template_id`: Foreign key → templates (CASCADE)
- `created_at`: Timestamp

#### `user_favorite_snippets`
Tabla de asociación many-to-many
- `user_id`: Foreign key → users (CASCADE)
- `snippet_id`: Foreign key → snippets (CASCADE)
- `created_at`: Timestamp

## Auditoría

### Eventos Auditados en Encounters

- **create**: Creación de nueva consulta
- **update**: Modificación de consulta
- **status_change**: Cambio de estado
- **delete**: Eliminación de consulta

**Metadata incluye:**
- `patient_id`
- `specialty`
- `status` (actual o anterior/nuevo)
- `updated_fields` (en updates)

## Instalación y Configuración

### 1. Aplicar Migraciones

```bash
# Aplicar migración de Sprint 3
alembic upgrade head
```

### 2. Poblar Base de Datos

```bash
# Ejecutar seed script para crear templates y snippets iniciales
python scripts/seed_data.py
```

**Seed incluye:**
- 3 templates (General Medicine, Pediatrics, Traumatology)
- 15 snippets distribuidos en todas las categorías

### 3. Verificar Instalación

```bash
# Iniciar servidor
python run.py

# Abrir documentación interactiva
# http://localhost:8000/docs
```

## Ejemplos de Uso

### Crear Consulta con Template

1. **GET** `/api/v1/templates/?specialty=GENERAL&only_favorites=true`
   - Obtener templates favoritos de medicina general

2. **POST** `/api/v1/encounters/`
   - Usar contenido del template como base
   - Editar según el caso específico

### Usar Snippets en Consulta

1. **GET** `/api/v1/snippets/?category=diagnosis&only_favorites=true`
   - Obtener snippets de diagnósticos favoritos

2. Copiar `content` del snippet deseado

3. Pegar en el campo `assessment` de la consulta

### Workflow Completo

```python
# 1. Crear consulta en borrador
encounter = POST /api/v1/encounters/
{
  "patient_id": 5,
  "specialty": "GENERAL",
  "status": "DRAFT"
}

# 2. Actualizar con contenido (usar template + snippets)
PUT /api/v1/encounters/{encounter_id}
{
  "subjective": "...",
  "objective": "...",
  "assessment": "...",  # Usar snippet de diagnóstico
  "plan": "..."          # Usar snippet de tratamiento
}

# 3. Marcar como en progreso
PATCH /api/v1/encounters/{encounter_id}/status
{ "new_status": "IN_PROGRESS" }

# 4. Finalizar consulta
PATCH /api/v1/encounters/{encounter_id}/status
{ "new_status": "COMPLETED" }
```

## Permisos por Rol

| Acción | ADMIN | DOCTOR | SECRETARIA |
|--------|-------|--------|------------|
| Crear encounter | ✅ | ✅ | ❌ |
| Ver encounters | ✅ | ✅ | ✅ |
| Editar encounter | ✅ | ✅ | ❌ |
| Crear template/snippet | ✅ | ✅ | ❌ |
| Ver templates/snippets | ✅ | ✅ | ✅ |
| Editar template/snippet | ✅ | ✅ | ❌ |
| Gestionar favoritos | ✅ | ✅ | ✅ |

## Validaciones

### Encounters
- `patient_id` debe existir
- `doctor_id` se asigna automáticamente al usuario actual
- `specialty` debe ser un valor válido del enum
- `status` debe ser un valor válido del enum

### Templates
- `title` obligatorio (1-255 caracteres)
- `specialty` debe ser un valor válido del enum
- Al menos un campo SOAP debe tener contenido

### Snippets
- `title` obligatorio (1-255 caracteres)
- `category` obligatorio (1-50 caracteres)
- `content` obligatorio
- `usage_count` se incrementa automáticamente al obtener snippet

## Mejores Prácticas

### 1. Uso de Templates
- Crear templates específicos por especialidad
- Incluir campos comunes pero dejar espacio para personalización
- Mantener templates actualizados con protocolos vigentes

### 2. Uso de Snippets
- Crear snippets para textos repetitivos (no para casos únicos)
- Usar categorías adecuadamente para facilitar búsqueda
- Monitorear `usage_count` para identificar snippets más útiles

### 3. Workflow de Consulta
- Iniciar en `DRAFT` para guardar progreso
- Usar `IN_PROGRESS` durante la consulta
- Solo marcar `COMPLETED` cuando esté finalizada
- Usar `CANCELLED` para consultas que no se completaron

### 4. Favoritos
- Marcar templates/snippets frecuentes como favoritos
- Revisar favoritos periódicamente y actualizar

## Troubleshooting

### Error: "Encounter with ID X not found"
**Solución:** Verificar que el ID de consulta existe y que tienes permisos para acceder

### Error: "Operation requires doctor or admin role"
**Solución:** Solo DOCTOR y ADMIN pueden crear/editar consultas

### Error: "Template/Snippet already in favorites"
**Solución:** El item ya está en favoritos, no es necesario agregarlo nuevamente

### Error: "Patient with ID X not found"
**Solución:** Verificar que el paciente existe antes de crear la consulta

## Testing

### Probar Endpoints

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=doctor&password=doctor123"

# Guardar token
TOKEN="<access_token>"

# Listar templates
curl http://localhost:8000/api/v1/templates \
  -H "Authorization: Bearer $TOKEN"

# Crear encounter
curl -X POST http://localhost:8000/api/v1/encounters \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "specialty": "GENERAL",
    "subjective": "Dolor de cabeza",
    "status": "DRAFT"
  }'

# Listar encounters del paciente
curl "http://localhost:8000/api/v1/encounters?patient_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

## Próximos Pasos (Sprint 4)

Posibles mejoras para futuros sprints:

1. **Frontend para Consultas**
   - Formulario SOAP con autocompletado de snippets
   - Selector de templates
   - Vista de historial de consultas del paciente

2. **Búsqueda Avanzada**
   - Búsqueda full-text en consultas
   - Filtros por fecha, especialidad, estado
   - Búsqueda de snippets por contenido

3. **Reportes**
   - Estadísticas de consultas por especialidad
   - Snippets más utilizados
   - Templates más populares

4. **Versionado**
   - Historial de cambios en consultas
   - Comparación de versiones
   - Restaurar versiones anteriores

5. **Colaboración**
   - Comentarios en consultas
   - Compartir templates entre usuarios
   - Templates institucionales (no editables por usuarios)

## Soporte

Para más información consulta:
- **Documentación API**: http://localhost:8000/docs
- **Sprint 1**: `README_MVP_SPRINT1.md`
- **Sprint 2**: `README_SPRINT2_FRONTEND.md`
- **Inicio Rápido**: `INICIO_SPRINT2.md`

---

**Versión:** Sprint 3
**Fecha:** 2026-01-05
**Estado:** Completado ✅
