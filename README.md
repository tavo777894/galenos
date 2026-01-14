# Historia Clínica Electrónica - MVP

Sistema profesional de Historia Clínica Electrónica desarrollado con FastAPI, PostgreSQL y arquitectura limpia.

## Características (Sprint 1)

- Autenticación JWT con roles (Doctor, Secretaria)
- CRUD completo de pacientes
- Generación de PDF de fichas de pacientes
- Base de datos con PostgreSQL y SQLite
- Migraciones con Alembic
- Validación con Pydantic
- Documentación automática con Swagger/ReDoc
- Arquitectura limpia y modular

## Tecnologías

- **Backend**: FastAPI 0.115.0
- **Base de datos**: PostgreSQL 16 / SQLite
- **ORM**: SQLAlchemy 2.0
- **Migraciones**: Alembic
- **Autenticación**: JWT (python-jose)
- **Seguridad**: Bcrypt (passlib)
- **PDF**: WeasyPrint + Jinja2
- **Validación**: Pydantic 2.10

## Estructura del Proyecto

```
galenos/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Endpoints de autenticación
│   │       │   └── patients.py      # Endpoints de pacientes
│   │       └── router.py            # Router principal de API
│   ├── core/
│   │   ├── config.py                # Configuración de la aplicación
│   │   ├── security.py              # Utilidades de seguridad (JWT, hash)
│   │   └── deps.py                  # Dependencias de FastAPI
│   ├── db/
│   │   └── session.py               # Configuración de base de datos
│   ├── models/
│   │   ├── user.py                  # Modelo de Usuario
│   │   └── patient.py               # Modelo de Paciente
│   ├── schemas/
│   │   ├── user.py                  # Schemas de Usuario
│   │   └── patient.py               # Schemas de Paciente
│   ├── services/
│   │   └── pdf_service.py           # Servicio de generación de PDF
│   ├── templates/
│   │   └── patient_card.html        # Template HTML para PDF
│   └── main.py                      # Punto de entrada de la aplicación
├── alembic/
│   ├── versions/                    # Migraciones de base de datos
│   ├── env.py                       # Configuración de Alembic
│   └── script.py.mako              # Template para migraciones
├── scripts/
│   └── seed_data.py                 # Script de datos iniciales
├── tests/                           # Tests (para desarrollo futuro)
├── .env.example                     # Ejemplo de variables de entorno
├── .gitignore                       # Archivos a ignorar en Git
├── alembic.ini                      # Configuración de Alembic
├── docker-compose.yml               # Configuración de Docker
├── requirements.txt                 # Dependencias de Python
└── README.md                        # Este archivo
```

## Instalación y Configuración

### Requisitos Previos

- Python 3.10 o superior
- Docker y Docker Compose (opcional, para PostgreSQL)
- Git

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd galenos
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Windows: WeasyPrint (MSYS2) Setup

1. Instala MSYS2 en `C:\msys64`
2. Abre la terminal **MSYS2 MINGW64**
3. Ejecuta:
   ```bash
   pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-cairo mingw-w64-x86_64-pango
   ```
4. Verifica con:
   ```bash
   python scripts/test_weasyprint_minimal.py
   ```

La aplicaci艠n ejecuta un self-test de WeasyPrint al iniciar: en `DEBUG=True` registra warning y contin俣a, en `DEBUG=False` falla r姘idamente si falta el runtime.

### 4. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
# IMPORTANTE: Cambiar SECRET_KEY en producción
```

Variables principales:
- `DATABASE_URL`: URL de conexión a la base de datos
- `SECRET_KEY`: Clave secreta para JWT (mínimo 32 caracteres)
- `CLINIC_NAME`: Nombre de tu clínica
- `CLINIC_ADDRESS`: Dirección de tu clínica
- `CLINIC_PHONE`: Teléfono de tu clínica

### 5. Configurar Base de Datos

#### Opción A: PostgreSQL con Docker (Recomendado)

```bash
# Iniciar PostgreSQL
docker-compose up -d

# Verificar que esté corriendo
docker-compose ps
```

Asegúrate de que tu `.env` tenga:
```
DATABASE_URL=postgresql://galenos_user:galenos_password@localhost:5432/galenos_db
```

#### Opción B: SQLite (Desarrollo)

En tu `.env`:
```
DATABASE_URL=sqlite:///./galenos.db
```

### 6. Crear Migración Inicial y Aplicar

```bash
# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

### 7. Cargar Datos Iniciales (Opcional)

```bash
python scripts/seed_data.py
```

Esto creará:
- Usuario Doctor (username: `doctor`, password: `doctor123`)
- Usuario Secretaria (username: `secretaria`, password: `secretaria123`)
- 3 pacientes de ejemplo


### Seed (clinico minimo)

Requisito:
- alembic upgrade head

Ejecutar:

```bash
python -m scripts.seed_clinical
```

Nota: `scripts/seed_data.py` es un seed masivo (opcional).

### 8. Ejecutar la Aplicación

```bash
# Modo desarrollo (con auto-reload)
uvicorn app.main:app --reload

# O usando Python directamente
python -m app.main
```

La aplicación estará disponible en: `http://localhost:8000`

## Uso de la API

### Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Autenticación

1. **Registrar un usuario**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@example.com",
    "username": "nuevo",
    "full_name": "Nuevo Usuario",
    "password": "password123",
    "role": "secretaria"
  }'
```

2. **Login** (obtener token):
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=doctor&password=doctor123"
```

Respuesta:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Gestión de Pacientes

**IMPORTANTE**: Todos los endpoints de pacientes requieren autenticación. Incluye el token en el header:
```
Authorization: Bearer <tu-token>
```

3. **Crear paciente**:
```bash
curl -X POST "http://localhost:8000/api/v1/patients/" \
  -H "Authorization: Bearer <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Pedro",
    "last_name": "Sánchez",
    "ci": "99887766",
    "date_of_birth": "1990-05-15",
    "phone": "+591 78901234",
    "email": "pedro@email.com",
    "address": "Calle Principal 789",
    "allergies": "Ninguna",
    "medical_history": "Paciente sano"
  }'
```

4. **Listar pacientes**:
```bash
curl -X GET "http://localhost:8000/api/v1/patients/" \
  -H "Authorization: Bearer <tu-token>"
```

5. **Obtener paciente por ID**:
```bash
curl -X GET "http://localhost:8000/api/v1/patients/1" \
  -H "Authorization: Bearer <tu-token>"
```

6. **Buscar paciente por CI**:
```bash
curl -X GET "http://localhost:8000/api/v1/patients/search/ci/12345678" \
  -H "Authorization: Bearer <tu-token>"
```

7. **Actualizar paciente**:
```bash
curl -X PUT "http://localhost:8000/api/v1/patients/1" \
  -H "Authorization: Bearer <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+591 79999999",
    "address": "Nueva dirección"
  }'
```

8. **Eliminar paciente**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/patients/1" \
  -H "Authorization: Bearer <tu-token>"
```

### Generación de PDF

9. **Generar ficha de paciente en PDF**:
```bash
curl -X GET "http://localhost:8000/api/v1/patients/1/pdf" \
  -H "Authorization: Bearer <tu-token>" \
  --output ficha_paciente.pdf
```

O visita directamente en el navegador (después de hacer login):
```
http://localhost:8000/api/v1/patients/1/pdf
```

## Roles y Permisos

- **Doctor**: Acceso completo a todos los endpoints
- **Secretaria**: Acceso completo a todos los endpoints

En futuras versiones se pueden añadir restricciones específicas por rol.

## Migraciones de Base de Datos

```bash
# Crear una nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones pendientes
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial de migraciones
alembic history

# Ver estado actual
alembic current
```

## Testing

```bash
# Ejecutar tests (cuando se implementen)
pytest

# Con coverage
pytest --cov=app tests/
```

## Desarrollo

### Activar modo debug

En `.env`:
```
DEBUG=True
```

### Hot reload

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Producción

### Configuración de Seguridad

1. **Generar SECRET_KEY seguro**:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Configurar variables de entorno**:
```bash
DEBUG=False
SECRET_KEY=<tu-clave-super-segura-generada>
DATABASE_URL=postgresql://user:password@host:5432/db
```

3. **Ejecutar con múltiples workers**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

O usar Gunicorn:
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### Error: "Could not validate credentials"
- Verifica que el token no haya expirado
- Asegúrate de incluir "Bearer " antes del token en el header

### Error de conexión a PostgreSQL
- Verifica que Docker esté corriendo: `docker-compose ps`
- Verifica la URL de conexión en `.env`
- Reinicia el contenedor: `docker-compose restart`

### Error al generar PDF
- Asegúrate de tener instaladas las dependencias de WeasyPrint
- En Windows, puede requerir GTK+: https://weasyprint.readthedocs.io/en/latest/install.html

### Error en migraciones Alembic
- Verifica que la base de datos esté accesible
- Revisa el archivo `alembic.ini`
- Verifica que los modelos estén importados en `alembic/env.py`

## Próximos Pasos (Sprint 2+)

- Gestión de consultas médicas
- Historial de consultas por paciente
- Prescripciones médicas
- Gestión de citas
- Dashboard con estadísticas
- Búsqueda avanzada de pacientes
- Exportación de reportes
- Sistema de notificaciones
- Tests unitarios y de integración
- CI/CD pipeline

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto es privado y confidencial.

## Contacto

Para preguntas o soporte, contacta al equipo de desarrollo.

---

Desarrollado con FastAPI y Python
