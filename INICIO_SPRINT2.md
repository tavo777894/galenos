# 🚀 Inicio Rápido - Sprint 2 (Frontend)

Guía para levantar el frontend web en menos de 5 minutos.

## Prerrequisitos

- ✅ Backend corriendo en `http://localhost:8000`
- ✅ Node.js 18+ instalado
- ✅ Base de datos con migraciones aplicadas

## Instalación en 4 Pasos

### 1️⃣ Instalar Dependencias del Frontend

```bash
cd frontend
npm install
```

### 2️⃣ Configurar Variables de Entorno

```bash
cp .env.example .env
```

El archivo `.env` ya viene configurado para desarrollo local.

### 3️⃣ Aplicar Migraciones de Búsqueda (Backend)

```bash
cd ..  # Volver a la raíz
alembic upgrade head
```

Esto aplicará los índices de búsqueda para mejor performance.

### 4️⃣ Ejecutar Frontend

```bash
cd frontend
npm run dev
```

¡Listo! Abre `http://localhost:3000`

## Estructura de Terminales

Necesitas 2 terminales abiertas:

### Terminal 1 - Backend
```bash
cd galenos
python run.py

# Debería mostrar:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Frontend
```bash
cd galenos/frontend
npm run dev

# Debería mostrar:
# VITE v5.1.0  ready in XXX ms
# ➜  Local:   http://localhost:3000/
```

## Login

1. Abre `http://localhost:3000`
2. Usa cualquiera de estas credenciales:

| Usuario | Password |
|---------|----------|
| doctor | doctor123 |
| secretaria | secretaria123 |
| admin | admin123 |

## Probar el Command Palette

### Opción 1: Atajo de Teclado

1. Una vez logueado, presiona `Ctrl+K` (Windows/Linux) o `⌘K` (Mac)
2. El Command Palette se abrirá
3. Escribe "carlos" para buscar pacientes
4. Navega con `↑` `↓`
5. Presiona `Enter` para ir al detalle

### Opción 2: Botón

1. Click en el botón "Buscar" en la barra superior
2. Mismo comportamiento que el atajo

## Casos de Uso Rápidos

### Buscar un Paciente

```
1. Ctrl+K
2. Escribe: "carlos"
3. Verás la lista de pacientes llamados Carlos
4. Enter para ir al detalle
```

### Acciones Rápidas

```
Ctrl+K → Sin escribir nada:
  - Nuevo Paciente
  - Ver Pacientes
  - Ver Documentos
```

### Búsqueda Contextual

```
Ctrl+K → "nuevo"     → Sugiere "Nuevo Paciente"
Ctrl+K → "documento" → Sugiere "Ver Documentos"
Ctrl+K → "consulta"  → Sugiere "Nueva Consulta"
```

### Ver Lista de Pacientes

```
1. Click en "Pacientes" en el sidebar
2. Verás todos los pacientes en cards
3. Usa la búsqueda local para filtrar
4. Click en un paciente para ver detalle
```

## Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+K` / `⌘K` | Abrir Command Palette |
| `↑` | Navegar hacia arriba |
| `↓` | Navegar hacia abajo |
| `Enter` | Seleccionar resultado |
| `ESC` | Cerrar Command Palette |

## Verificar que Todo Funciona

### Backend

```bash
# En otra terminal:
curl http://localhost:8000/health

# Debería responder:
# {"status":"healthy"}
```

### Frontend

```bash
# Verificar que Vite esté corriendo
curl http://localhost:3000

# Debería retornar HTML
```

### Búsqueda

```bash
# Login primero y obtén el token
TOKEN="tu_access_token_aqui"

# Probar endpoint de búsqueda
curl http://localhost:8000/api/v1/search?q=carlos \
  -H "Authorization: Bearer $TOKEN"

# Debería retornar JSON con pacientes y acciones
```

## Troubleshooting Rápido

### "Cannot GET /api/v1/patients"

**Problema**: Backend no está corriendo

**Solución**:
```bash
cd galenos
python run.py
```

### "Network Error" en el frontend

**Problema**: Backend no responde o CORS bloqueado

**Solución**:
1. Verifica que el backend esté en `http://localhost:8000`
2. Verifica `.env` en backend incluya `http://localhost:3000` en CORS

### "401 Unauthorized" al buscar

**Problema**: Token expirado o inválido

**Solución**:
```javascript
// En la consola del navegador (F12):
localStorage.clear()
// Luego haz login nuevamente
```

### Command Palette no abre con Ctrl+K

**Problema**: Otro programa usa el mismo atajo

**Solución**:
- Click en el botón "Buscar" en el header
- Cierra otras aplicaciones que usen Ctrl+K (ej: VS Code)

### Frontend muy lento

**Problema**: Modo de desarrollo de Vite

**Solución**:
```bash
# Build para producción (mucho más rápido)
npm run build
npm run preview
```

## Siguiente Paso

Revisa la documentación completa:

- **Frontend**: `frontend/README.md`
- **Sprint 2**: `README_SPRINT2_FRONTEND.md`
- **Backend**: `README_MVP_SPRINT1.md`

## Tips

💡 **Command Palette es tu amigo**: Úsalo constantemente, es más rápido que navegar con el mouse.

💡 **Búsqueda inteligente**: El Command Palette sugiere acciones según lo que escribes.

💡 **Keyboard-first**: Todo está optimizado para usar con teclado, incluyendo navegación por resultados.

💡 **Real-time search**: Los resultados aparecen mientras escribes (con 300ms de debounce para no saturar el servidor).

---

**¡Listo para desarrollar!** 🎉

Si tienes problemas, revisa la sección de Troubleshooting en `README_SPRINT2_FRONTEND.md`
