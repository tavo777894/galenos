# Galenos Frontend

Frontend web para el sistema de Historia Clínica Electrónica.

## Tecnologías

- **React** 18.2 - UI library
- **Vite** 5.1 - Build tool
- **Tailwind CSS** 3.4 - Styling
- **React Router** 6.22 - Routing
- **Axios** - HTTP client
- **cmdk** - Command Palette component
- **Lucide React** - Icons

## Características

### ✨ Implementado en Sprint 2

- ✅ Autenticación JWT con tokens de acceso y refresco
- ✅ Layout responsivo con sidebar y navegación
- ✅ Página de login con credenciales de prueba
- ✅ Lista de pacientes con búsqueda
- ✅ **Command Palette** (Ctrl+K / ⌘K):
  - Búsqueda global en tiempo real
  - Navegación por teclado (↑ ↓ Enter ESC)
  - Acciones rápidas contextuales
  - Resultados de pacientes con detalles

### 🔐 Autenticación

- Almacenamiento en `localStorage`:
  - `access_token` - Token de acceso (30 min)
  - `refresh_token` - Token de refresco (7 días)
  - `user` - Datos básicos del usuario

- Renovación automática de tokens en interceptor de Axios
- Redirección automática a login si el refresh falla
- Manejo robusto de errores 401

## Instalación

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita `.env` si necesitas cambiar la URL del API:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Ejecutar en modo desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

## Scripts Disponibles

```bash
npm run dev      # Ejecutar en modo desarrollo
npm run build    # Build para producción
npm run preview  # Preview del build de producción
npm run lint     # Ejecutar ESLint
```

## Estructura del Proyecto

```
frontend/
├── public/                 # Archivos estáticos
├── src/
│   ├── components/         # Componentes reutilizables
│   │   ├── CommandPalette.jsx
│   │   └── Layout.jsx
│   ├── context/            # Contextos de React
│   │   └── AuthContext.jsx
│   ├── pages/              # Páginas/rutas
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── PatientList.jsx
│   │   └── Documents.jsx
│   ├── services/           # Servicios API
│   │   └── api.js
│   ├── utils/              # Utilidades
│   │   └── cn.js
│   ├── App.jsx             # Componente principal
│   ├── main.jsx            # Punto de entrada
│   └── index.css           # Estilos globales
├── .env.example            # Ejemplo de variables
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Uso

### Login

1. Abre `http://localhost:3000`
2. Usa una de las credenciales de prueba:
   - **Admin**: admin / admin123
   - **Doctor**: doctor / doctor123
   - **Secretaria**: secretaria / secretaria123

### Command Palette

El Command Palette es un buscador global estilo VS Code:

#### Atajos de teclado:

- `Ctrl+K` (Windows/Linux) o `⌘K` (Mac) - Abrir/cerrar
- `↑` `↓` - Navegar por resultados
- `Enter` - Seleccionar resultado
- `ESC` - Cerrar

#### Funcionalidades:

1. **Acciones Rápidas** (sin búsqueda):
   - Nuevo Paciente
   - Ver Pacientes
   - Ver Documentos

2. **Búsqueda de Pacientes**:
   - Por nombre (parcial, case-insensitive)
   - Por CI (exacto o parcial)
   - Muestra: nombre, CI, teléfono
   - Click o Enter para ir al detalle

3. **Acciones Contextuales**:
   - Aparecen según palabras clave en la búsqueda
   - Ejemplos: "nuevo", "paciente", "documento", "consulta"

### Navegación

El sidebar incluye:

- **Inicio** - Dashboard con estadísticas
- **Pacientes** - Lista completa de pacientes
- **Documentos** - Historial de documentos (próximamente)

### Manejo de Errores

El frontend maneja errores de forma clara:

- **401 Unauthorized** - Intenta refresh automático, luego redirige a login
- **500 Server Error** - Mensaje de error visible al usuario
- **Network Error** - Mensaje de conexión fallida

## Proxy de Desarrollo

Vite está configurado para hacer proxy de `/api` a `http://localhost:8000`:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

Esto evita problemas de CORS en desarrollo.

## Despliegue

### Build para producción

```bash
npm run build
```

Los archivos optimizados estarán en `dist/`.

### Variables de entorno en producción

Asegúrate de configurar `VITE_API_URL` con la URL de tu API en producción.

### Servir archivos estáticos

Puedes servir los archivos de `dist/` con cualquier servidor estático:

```bash
# Con serve
npm install -g serve
serve -s dist -l 3000

# Con nginx
# Configura nginx para servir dist/ y proxy /api a tu backend
```

## Próximos Pasos (Sprint 3+)

- Página de detalle de paciente
- Formulario de creación/edición de paciente
- Gestión de documentos
- Gestión de consultas médicas
- Dashboard con estadísticas reales
- Notificaciones en tiempo real
- Tests unitarios (Jest + React Testing Library)
- Tests E2E (Playwright)

## Troubleshooting

### El frontend no se conecta al backend

1. Verifica que el backend esté corriendo en `http://localhost:8000`
2. Verifica `VITE_API_URL` en `.env`
3. Verifica la configuración de CORS en el backend

### Errores 401 continuos

1. Verifica que las credenciales sean correctas
2. Limpia localStorage: `localStorage.clear()`
3. Verifica que el SECRET_KEY del backend no haya cambiado

### Command Palette no abre con Ctrl+K

1. Verifica que no haya otro atajo de teclado interfiriendo
2. Prueba con `⌘K` si estás en Mac
3. Click en el botón "Buscar" en la barra superior

## Recursos

- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [cmdk](https://cmdk.paco.me/)
- [React Router](https://reactrouter.com/)

---

**Desarrollado para Galenos - Historia Clínica Electrónica**
