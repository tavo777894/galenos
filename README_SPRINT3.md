# Sprint 3: Consultas Clínicas SOAP con Templates y Snippets

## Resumen Ejecutivo

Sprint 3 implementa un sistema completo de consultas clínicas médicas usando formato SOAP (Subjective, Objective, Assessment, Plan), con plantillas reutilizables y fragmentos de texto (snippets) para las especialidades: **CARDIOLOGIA**, **NEUROLOGIA**, **DERMATOLOGIA**, y **CIRUGIA_CARDIOVASCULAR**.

## Especialidades Médicas

El sistema soporta 4 especialidades médicas principales:

```python
class MedicalSpecialty(str, enum.Enum):
    CARDIOLOGIA = "CARDIOLOGIA"
    NEUROLOGIA = "NEUROLOGIA"
    DERMATOLOGIA = "DERMATOLOGIA"
    CIRUGIA_CARDIOVASCULAR = "CIRUGIA_CARDIOVASCULAR"
```

## Estados de Consulta

```python
class EncounterStatus(str, enum.Enum):
    DRAFT = "DRAFT"      # Borrador - en edición
    SIGNED = "SIGNED"    # Firmada - finalizada
```

## Categorías de Snippets

Los snippets están organizados en 6 categorías clínicas:

```python
class SnippetCategory(str):
    MOTIVO = "MOTIVO"                    # Motivo de consulta
    ANTECEDENTES = "ANTECEDENTES"        # Antecedentes médicos
    EXAMEN = "EXAMEN"                    # Hallazgos de examen físico
    DX = "DX"                            # Diagnósticos
    PLAN = "PLAN"                        # Planes de tratamiento
    INDICACIONES = "INDICACIONES"        # Indicaciones al paciente
```

## Arquitectura de Base de Datos

### Tabla: `encounters`

Almacena las consultas clínicas en formato SOAP.

```sql
CREATE TABLE encounters (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,  -- FK a patients
    doctor_id INTEGER NOT NULL,   -- FK a users
    specialty ENUM NOT NULL,      -- Especialidad médica
    status ENUM NOT NULL,         -- DRAFT o SIGNED
    subjective TEXT,              -- S: Síntomas del paciente
    objective TEXT,               -- O: Hallazgos objetivos
    assessment TEXT,              -- A: Diagnóstico
    plan TEXT,                    -- P: Plan de tratamiento
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

**Índices:**
- `ix_encounters_patient_id`
- `ix_encounters_doctor_id`
- `ix_encounters_created_at`

### Tabla: `templates`

Plantillas predefinidas con contenido por defecto para cada sección SOAP.

```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    specialty ENUM NOT NULL,
    default_subjective TEXT,
    default_objective TEXT,
    default_assessment TEXT,
    default_plan TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME
);
```

**Índice:** `ix_templates_specialty`

### Tabla: `snippets`

Fragmentos de texto reutilizables por especialidad y categoría.

```sql
CREATE TABLE snippets (
    id INTEGER PRIMARY KEY,
    specialty ENUM NOT NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    usage_count INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME
);
```

**Índices:**
- `ix_snippets_specialty`
- `ix_snippets_category`

### Tablas de Favoritos (Many-to-Many)

```sql
CREATE TABLE user_favorite_templates (
    user_id INTEGER PRIMARY KEY,
    template_id INTEGER PRIMARY KEY,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
);

CREATE TABLE user_favorite_snippets (
    user_id INTEGER PRIMARY KEY,
    snippet_id INTEGER PRIMARY KEY,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE
);
```

## API Endpoints

### Encounters (Consultas Clínicas)

#### `POST /api/v1/encounters/`
**Crear nueva consulta**

**Roles:** DOCTOR, ADMIN

**Request Body:**
```json
{
  "patient_id": 1,
  "specialty": "CARDIOLOGIA",
  "subjective": "Dolor precordial de 2 horas...",
  "objective": "PA: 140/90, FC: 88...",
  "assessment": "Síndrome coronario agudo probable",
  "plan": "Hospitalización, ECG, troponinas...",
  "status": "DRAFT"
}
```

**Response:** `201 Created`

---

#### `GET /api/v1/encounters/`
**Listar todas las consultas**

**Roles:** Todos los autenticados

**Query Params:**
- `patient_id` (opcional): Filtrar por ID de paciente
- `skip`: Paginación offset (default: 0)
- `limit`: Cantidad de resultados (default: 100, max: 500)

---

#### `GET /api/v1/patients/{patient_id}/encounters`
**Listar consultas de un paciente específico**

**Roles:** Todos los autenticados

**Query Params:**
- `skip`, `limit`: Paginación

**Response:** Lista de encounters ordenadas por fecha (más reciente primero)

---

#### `GET /api/v1/encounters/{encounter_id}`
**Obtener detalle de consulta**

**Roles:** Todos los autenticados

**Response:** Encounter con detalles de paciente y doctor

---

#### `PUT /api/v1/encounters/{encounter_id}`
**Actualizar consulta**

**Roles:** DOCTOR, ADMIN

**Request Body:** Campos a actualizar (parcial)

---

#### `PATCH /api/v1/encounters/{encounter_id}/status`
**Cambiar estado de consulta**

**Roles:** DOCTOR, ADMIN

**Request Body:**
```json
{
  "new_status": "SIGNED"
}
```

---

#### `POST /api/v1/encounters/{encounter_id}/apply-template/{template_id}`
**Aplicar plantilla a consulta**

**Roles:** DOCTOR, ADMIN

**Comportamiento:**
- Copia el contenido de los campos default del template al encounter
- Verifica que la especialidad del template coincida con la del encounter
- Registra acción `APPLY_TEMPLATE` en auditoría con metadata:
  ```json
  {
    "template_id": 1,
    "patient_id": 5,
    "template_title": "Consulta Cardiológica"
  }
  ```

**Response:** Encounter actualizado

---

#### `DELETE /api/v1/encounters/{encounter_id}`
**Eliminar consulta** (soft delete → status = CANCELLED)

**Roles:** DOCTOR, ADMIN

---

### Templates (Plantillas)

#### `GET /api/v1/templates/`
**Listar plantillas**

**Roles:** Todos los autenticados

**Query Params:**
- `specialty` (opcional): Filtrar por especialidad (ej: `CARDIOLOGIA`)
- `only_active` (default: true): Solo plantillas activas
- `only_favorites` (default: false): Solo favoritos del usuario
- `skip`, `limit`: Paginación

**Response:** Lista con flag `is_favorite` para cada template

---

#### `GET /api/v1/templates/{template_id}`
**Obtener plantilla específica**

**Response:** Template con flag `is_favorite`

---

#### `POST /api/v1/templates/`
**Crear plantilla**

**Roles:** DOCTOR, ADMIN

---

#### `PUT /api/v1/templates/{template_id}`
**Actualizar plantilla**

**Roles:** DOCTOR, ADMIN

---

#### `DELETE /api/v1/templates/{template_id}`
**Desactivar plantilla** (soft delete → `is_active = 0`)

**Roles:** DOCTOR, ADMIN

---

### Snippets (Fragmentos de Texto)

#### `GET /api/v1/snippets/`
**Listar snippets**

**Roles:** Todos los autenticados

**Query Params:**
- `specialty` (opcional): Filtrar por especialidad
- `category` (opcional): Filtrar por categoría (ej: `DX`)
- `only_active` (default: true): Solo snippets activos
- `only_favorites` (default: false): Solo favoritos del usuario
- `skip`, `limit`: Paginación

**Ordenamiento:** Por `usage_count DESC, title ASC`

**Response:** Lista con flag `is_favorite` para cada snippet

---

#### `GET /api/v1/snippets/{snippet_id}`
**Obtener snippet específico**

**Comportamiento:** Incrementa automáticamente `usage_count`

**Response:** Snippet con flag `is_favorite`

---

#### `POST /api/v1/snippets/`
**Crear snippet**

**Roles:** DOCTOR, ADMIN

**Request Body:**
```json
{
  "specialty": "CARDIOLOGIA",
  "title": "Fibrilación auricular",
  "category": "DX",
  "content": "Fibrilación auricular de novo...",
  "is_active": 1
}
```

---

#### `PUT /api/v1/snippets/{snippet_id}`
**Actualizar snippet**

**Roles:** DOCTOR, ADMIN

---

#### `DELETE /api/v1/snippets/{snippet_id}`
**Desactivar snippet** (soft delete → `is_active = 0`)

**Roles:** DOCTOR, ADMIN

---

### Favorites (Favoritos)

#### `POST /api/v1/favorites/templates/{template_id}`
**Agregar plantilla a favoritos**

**Roles:** Todos los autenticados

**Response:** `204 No Content`

---

#### `DELETE /api/v1/favorites/templates/{template_id}`
**Remover plantilla de favoritos**

**Roles:** Todos los autenticados

**Response:** `204 No Content`

---

#### `POST /api/v1/favorites/snippets/{snippet_id}`
**Agregar snippet a favoritos**

**Roles:** Todos los autenticados

**Response:** `204 No Content`

---

#### `DELETE /api/v1/favorites/snippets/{snippet_id}`
**Remover snippet de favoritos**

**Roles:** Todos los autenticados

**Response:** `204 No Content`

---

## Sistema de Auditoría

### Eventos Auditados

| Entidad | Acción | Metadata |
|---------|--------|----------|
| encounter | create | patient_id, specialty, status |
| encounter | update | patient_id, updated_fields |
| encounter | status_change | patient_id, old_status, new_status |
| encounter | delete | patient_id |
| encounter | **APPLY_TEMPLATE** | **template_id, patient_id, template_title** |

La acción `APPLY_TEMPLATE` es exclusiva de Sprint 3 y registra cuando un médico aplica una plantilla a una consulta.

## Data Seeds

El script de seeds (`scripts/seed_data.py`) crea:

### 4 Templates Profesionales

1. **CARDIOLOGIA**: Consulta Cardiológica - Evaluación Cardiovascular
2. **NEUROLOGIA**: Consulta Neurológica - Evaluación Neurológica
3. **DERMATOLOGIA**: Consulta Dermatológica - Evaluación Cutánea
4. **CIRUGIA_CARDIOVASCULAR**: Consulta Cirugía Cardiovascular - Evaluación Quirúrgica

### 60 Snippets Profesionales (15 por especialidad)

Distribuidos en las 6 categorías:
- **MOTIVO**: 3 snippets
- **ANTECEDENTES**: 2 snippets
- **EXAMEN**: 3 snippets
- **DX**: 3 snippets
- **PLAN**: 2 snippets
- **INDICACIONES**: 2 snippets

**Ejemplos por especialidad:**

**CARDIOLOGIA:**
- Dolor precordial, Disnea de esfuerzo, Síndrome coronario agudo, Manejo IC, etc.

**NEUROLOGIA:**
- Cefalea intensa, Déficit motor, ACV isquémico, Manejo crisis convulsiva, etc.

**DERMATOLOGIA:**
- Lesión cutánea pruriginosa, Melanoma sospechoso, Tratamiento dermatitis, etc.

**CIRUGIA_CARDIOVASCULAR:**
- Claudicación intermitente, Estenosis aórtica severa, CABG programada, etc.

## Instalación y Setup

### 1. Aplicar Migraciones

```bash
alembic upgrade head
```

Esto creará las tablas:
- `encounters`
- `templates`
- `snippets`
- `user_favorite_templates`
- `user_favorite_snippets`

### 2. Poblar Base de Datos con Seeds

```bash
python scripts/seed_data.py
```

Creará:
- 4 templates (1 por especialidad)
- 60 snippets (15 por especialidad)
- Usuarios existentes: admin, doctor, secretaria
- 5 pacientes de ejemplo

### 3. Iniciar Servidor

```bash
python run.py
```

### 4. Probar Endpoints

Abre la documentación interactiva Swagger: `http://localhost:8000/docs`

## Tests Smoke

Se incluyen tests básicos en `tests/test_sprint3_smoke.py`:

```bash
pytest tests/test_sprint3_smoke.py -v
```

**Tests incluidos:**
1. ✓ Crear encounter
2. ✓ Listar encounters por paciente
3. ✓ Listar templates
4. ✓ Listar templates por especialidad
5. ✓ Listar snippets
6. ✓ Listar snippets por especialidad y categoría
7. ✓ Aplicar template a encounter (verifica auditoría)
8. ✓ Endpoints de favoritos (add/remove)

## Permisos por Rol

| Acción | ADMIN | DOCTOR | SECRETARIA |
|--------|-------|--------|------------|
| Crear encounter | ✅ | ✅ | ❌ |
| Ver encounters | ✅ | ✅ | ✅ |
| Editar encounter | ✅ | ✅ | ❌ |
| Aplicar template | ✅ | ✅ | ❌ |
| Crear template/snippet | ✅ | ✅ | ❌ |
| Ver templates/snippets | ✅ | ✅ | ✅ |
| Editar template/snippet | ✅ | ✅ | ❌ |
| Gestionar favoritos | ✅ | ✅ | ✅ |

## Ejemplos de Uso

### Workflow Completo de Consulta

```bash
# 1. Login como doctor
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=doctor&password=doctor123"

TOKEN="<access_token>"

# 2. Crear encounter en borrador
curl -X POST http://localhost:8000/api/v1/encounters \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "specialty": "CARDIOLOGIA",
    "status": "DRAFT"
  }'

# Respuesta: encounter_id = 1

# 3. Aplicar template a encounter
curl -X POST http://localhost:8000/api/v1/encounters/1/apply-template/1 \
  -H "Authorization: Bearer $TOKEN"

# 4. Editar contenido SOAP
curl -X PUT http://localhost:8000/api/v1/encounters/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subjective": "Dolor precordial opresivo...",
    "objective": "PA: 140/90, FC: 88...",
    "assessment": "Angina inestable",
    "plan": "Hospitalización, ECG urgente..."
  }'

# 5. Firmar encounter
curl -X PATCH http://localhost:8000/api/v1/encounters/1/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_status": "SIGNED"}'

# 6. Ver historial de encounters del paciente
curl http://localhost:8000/api/v1/patients/1/encounters \
  -H "Authorization: Bearer $TOKEN"
```

### Uso de Snippets

```bash
# 1. Listar snippets de diagnóstico cardiovascular
curl "http://localhost:8000/api/v1/snippets?specialty=CARDIOLOGIA&category=DX" \
  -H "Authorization: Bearer $TOKEN"

# 2. Obtener snippet específico (incrementa usage_count)
curl http://localhost:8000/api/v1/snippets/5 \
  -H "Authorization: Bearer $TOKEN"

# 3. Agregar a favoritos
curl -X POST http://localhost:8000/api/v1/favorites/snippets/5 \
  -H "Authorization: Bearer $TOKEN"

# 4. Listar solo favoritos
curl "http://localhost:8000/api/v1/snippets?only_favorites=true" \
  -H "Authorization: Bearer $TOKEN"
```

## Validaciones

### Encounters
- `patient_id` debe existir en la base de datos
- `specialty` debe ser uno de los 4 valores del enum
- `status` debe ser DRAFT o SIGNED
- Al aplicar template, la especialidad debe coincidir

### Templates
- `title` obligatorio (1-255 caracteres)
- `specialty` obligatorio y válido
- Al menos un campo SOAP default recomendado

### Snippets
- `specialty` obligatorio y válido
- `title` obligatorio (1-255 caracteres)
- `category` obligatorio (1-50 caracteres)
- `content` obligatorio
- `usage_count` se incrementa automáticamente al obtener el snippet

## Mejores Prácticas

1. **Usar templates**: Iniciar consultas aplicando templates ahorra tiempo
2. **Especialidades correctas**: Siempre crear encounters con la especialidad adecuada
3. **Favoritos**: Marcar templates/snippets frecuentes para acceso rápido
4. **Snippets por categoría**: Organizar snippets usando las 6 categorías estándar
5. **Estados**: Mantener encounters en DRAFT hasta finalizar, luego SIGNED
6. **Auditoría**: Revisar audit_logs para seguimiento de aplicación de templates

## Troubleshooting

### Error: "Template specialty does not match encounter specialty"
**Causa:** Intentaste aplicar un template de una especialidad a un encounter de otra

**Solución:** Verifica que ambos tengan la misma especialidad

---

### Error: "Patient with ID X not found"
**Causa:** El patient_id no existe

**Solución:** Verifica el ID del paciente antes de crear el encounter

---

### Error: "Operation requires doctor or admin role"
**Causa:** Usuario SECRETARIA intentó crear/editar encounter

**Solución:** Usa credenciales de DOCTOR o ADMIN

---

## Stack Tecnológico

- **Backend**: FastAPI 0.109
- **ORM**: SQLAlchemy 2.0
- **Migraciones**: Alembic
- **Validación**: Pydantic 2.x
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Testing**: pytest
- **Autenticación**: JWT con roles

## Archivos Clave

```
galenos/
├── app/
│   ├── models/
│   │   ├── encounter.py          # Modelo Encounter + Enums
│   │   ├── template.py           # Modelo Template + favoritos
│   │   └── snippet.py            # Modelo Snippet + favoritos
│   ├── schemas/
│   │   ├── encounter.py          # Schemas Pydantic Encounter
│   │   ├── template.py           # Schemas Pydantic Template
│   │   └── snippet.py            # Schemas Pydantic Snippet
│   ├── api/v1/endpoints/
│   │   ├── encounters.py         # 6 endpoints + apply-template
│   │   ├── templates.py          # CRUD templates
│   │   ├── snippets.py           # CRUD snippets
│   │   ├── favorites.py          # Endpoints favoritos
│   │   └── patients.py           # + GET /{id}/encounters
│   └── services/
│       └── audit_service.py      # + log_apply_template()
├── alembic/versions/
│   └── 2026_01_05_add_sprint3_tables.py  # Migración Sprint 3
├── scripts/
│   └── seed_data.py              # Seeds: 4 templates + 60 snippets
├── tests/
│   └── test_sprint3_smoke.py     # Tests smoke
└── README_SPRINT3.md             # Este archivo
```

## Próximos Pasos

Posibles mejoras para Sprint 4:

1. **Frontend**: Interfaz web para gestión de encounters
2. **Búsqueda avanzada**: Full-text search en encounters
3. **Exportar a PDF**: Generar PDF de encounters firmados
4. **Firma digital**: Integración de firma electrónica real
5. **Versionado**: Historial de cambios en encounters
6. **Autocompletado**: Sugerencias de snippets mientras se escribe
7. **Estadísticas**: Dashboard con métricas de consultas por especialidad

---

**Sprint 3 Completado** ✅

**Fecha:** 2026-01-05
**Versión:** 1.0.0
