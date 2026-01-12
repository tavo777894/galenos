# Guía Rápida de Inicio

Esta guía te llevará de 0 a una aplicación funcionando en menos de 5 minutos.

## Inicio Rápido (SQLite)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Crear las tablas de la base de datos

```bash
# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migración
alembic upgrade head
```

### 3. Cargar datos de prueba

```bash
python scripts/seed_data.py
```

### 4. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en: http://localhost:8000

## Probar la API

### 1. Ver la documentación interactiva

Abre en tu navegador: http://localhost:8000/docs

### 2. Login

En la documentación de Swagger:

1. Busca el endpoint `POST /api/v1/auth/login`
2. Click en "Try it out"
3. Ingresa:
   - Username: `doctor`
   - Password: `doctor123`
4. Click en "Execute"
5. Copia el `access_token` de la respuesta

### 3. Autorizar tus peticiones

1. Click en el botón "Authorize" en la parte superior
2. Pega el token que copiaste
3. Click en "Authorize"

### 4. Probar endpoints de pacientes

Ahora puedes probar todos los endpoints:

- `GET /api/v1/patients/` - Listar pacientes
- `GET /api/v1/patients/1` - Ver un paciente específico
- `GET /api/v1/patients/1/pdf` - Generar PDF de la ficha del paciente
- `POST /api/v1/patients/` - Crear nuevo paciente
- `PUT /api/v1/patients/1` - Actualizar paciente
- `DELETE /api/v1/patients/1` - Eliminar paciente

## Usuarios de Prueba

Después de ejecutar el seed script tendrás:

**Doctor:**
- Username: `doctor`
- Password: `doctor123`
- Email: doctor@galenos.com

**Secretaria:**
- Username: `secretaria`
- Password: `secretaria123`
- Email: secretaria@galenos.com

## Usar PostgreSQL (Opcional)

Si prefieres usar PostgreSQL en lugar de SQLite:

### 1. Iniciar PostgreSQL con Docker

```bash
docker-compose up -d
```

### 2. Actualizar .env

Edita el archivo `.env` y cambia:

```
# DATABASE_URL=sqlite:///./galenos.db
DATABASE_URL=postgresql://galenos_user:galenos_password@localhost:5432/galenos_db
```

### 3. Ejecutar migraciones

```bash
alembic upgrade head
```

### 4. Cargar datos

```bash
python scripts/seed_data.py
```

### 5. Ejecutar aplicación

```bash
python run.py
```

## Comandos Útiles

```bash
# Ver logs de PostgreSQL
docker-compose logs -f postgres

# Detener PostgreSQL
docker-compose down

# Reiniciar PostgreSQL (sin perder datos)
docker-compose restart

# Eliminar todo (incluyendo datos)
docker-compose down -v
```

## Siguiente Paso

Lee el [README.md](README.md) completo para información detallada sobre:
- Arquitectura del proyecto
- Endpoints disponibles
- Configuración avanzada
- Despliegue en producción

## Problemas Comunes

### Error: "No module named 'app'"

Asegúrate de estar en el directorio raíz del proyecto (`galenos/`).

### Error al instalar WeasyPrint

WeasyPrint requiere dependencias del sistema. Consulta:
https://weasyprint.readthedocs.io/en/latest/install.html

**Windows**: Puede requerir GTK+

### Puerto 8000 ya en uso

Usa otro puerto:
```bash
uvicorn app.main:app --port 8001
```

O en `run.py` cambia el puerto.
