# 🚀 Inicio Rápido - MVP Sprint 1

## Instalación en 5 Pasos

### 1️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Inicializar Base de Datos

```bash
# Crear migración
alembic revision --autogenerate -m "Initial migration"

# Aplicar migración
alembic upgrade head

# Cargar datos de prueba (3 usuarios + 5 pacientes)
python scripts/seed_data.py
```

### 3️⃣ Ejecutar Servidor

```bash
python run.py
```

### 4️⃣ Acceder a Documentación Interactiva

Abre en tu navegador:
```
http://localhost:8000/docs
```

### 5️⃣ Probar el Sistema

#### Login

1. En Swagger UI, ve a `POST /api/v1/auth/login`
2. Click en "Try it out"
3. Ingresa:
   - Username: `doctor`
   - Password: `doctor123`
4. Click "Execute"
5. Copia el `access_token` de la respuesta

#### Autorizar Peticiones

1. Click en el botón "Authorize" (candado) en la parte superior
2. Pega el token
3. Click "Authorize"

#### Generar PDF de Paciente

1. Ve a `POST /api/v1/patients/{patient_id}/generate-card`
2. Ingresa `patient_id`: `1`
3. Click "Execute"
4. Copia el `download_url` de la respuesta

#### Descargar PDF

1. Ve a `GET /api/v1/documents/{document_id}/download`
2. Usa el `document_id` que obtuviste
3. Click "Execute"
4. Click "Download file"

## 📋 Credenciales

| Usuario | Password | Rol |
|---------|----------|-----|
| admin | admin123 | ADMIN |
| doctor | doctor123 | DOCTOR |
| secretaria | secretaria123 | SECRETARIA |

## 🎯 Casos de Uso Rápidos

### Crear un Paciente

```bash
POST /api/v1/patients/
```

```json
{
  "first_name": "Pedro",
  "last_name": "González",
  "ci": "98765432",
  "date_of_birth": "1990-03-20",
  "phone": "+591 79999999",
  "address": "Calle Nueva 456",
  "emergency_contact_name": "Ana González",
  "emergency_contact_phone": "+591 79999998",
  "emergency_contact_relationship": "Hermana",
  "allergies": "Ninguna",
  "medical_history": "Sin antecedentes"
}
```

### Listar Pacientes

```bash
GET /api/v1/patients/
```

### Buscar por CI

```bash
GET /api/v1/patients/search/ci/12345678
```

### Generar Ficha PDF

```bash
POST /api/v1/patients/1/generate-card
```

### Listar Documentos Generados

```bash
GET /api/v1/documents/?patient_id=1
```

### Reimprimir Documento

```bash
POST /api/v1/documents/1/reprint
```

## 🔄 Refresh Token

Cuando tu `access_token` expire (30 min):

```bash
POST /api/v1/auth/refresh
```

```json
{
  "refresh_token": "tu_refresh_token_aqui"
}
```

Obtendrás un nuevo `access_token` sin necesidad de hacer login nuevamente.

## 🐳 Usar PostgreSQL (Opcional)

Si prefieres PostgreSQL en lugar de SQLite:

```bash
# Iniciar PostgreSQL
docker-compose up -d

# Editar .env
# Descomentar: DATABASE_URL=postgresql://...
# Comentar: DATABASE_URL=sqlite://...

# Aplicar migraciones
alembic upgrade head

# Cargar seeds
python scripts/seed_data.py

# Ejecutar
python run.py
```

## 📖 Documentación Completa

- Ver `README_MVP_SPRINT1.md` para documentación detallada
- Ver `README.md` para información original del proyecto

## ❓ Problemas Comunes

### Error: "No module named 'app'"

Asegúrate de estar en el directorio raíz del proyecto:
```bash
cd D:\galenos
```

### Error: "Could not validate credentials"

El token expiró. Usa el endpoint `/refresh` o haz login nuevamente.

### Error al generar PDF

WeasyPrint requiere dependencias del sistema. En Windows, puede necesitar GTK+:
https://weasyprint.readthedocs.io/en/latest/install.html

### Puerto 8000 en uso

Cambia el puerto en `run.py` o usa:
```bash
uvicorn app.main:app --port 8001
```

## 🎉 ¡Listo!

Ahora tienes un sistema profesional de Historia Clínica Electrónica funcionando con:
- ✅ Autenticación JWT (access + refresh tokens)
- ✅ 3 roles de usuario (ADMIN, DOCTOR, SECRETARIA)
- ✅ Sistema de auditoría completo
- ✅ Gestión de pacientes con contacto de emergencia
- ✅ Generación de PDFs profesionales con logo
- ✅ Historial de documentos con hash de integridad
- ✅ Endpoints de descarga y reimpresión

**Siguiente paso**: Explora la documentación completa en `README_MVP_SPRINT1.md`
