# 🎯 Plataforma de Gestión de Eventos

Una aplicación web completa desarrollada en Django para gestionar eventos como conferencias, conciertos y seminarios, con un sistema robusto de autenticación y autorización.

## 🚀 Características Principales

### Sistema de Autenticación y Autorización
- **Registro e inicio de sesión** de usuarios
- **Sistema de grupos** con roles específicos:
  - **Administradores**: Control total del sistema
  - **Organizadores**: Crear y gestionar eventos
  - **Asistentes**: Ver y registrarse en eventos
- **Permisos granulares** usando Django Auth
- **Eventos privados** con acceso controlado

### Gestión de Eventos
- **CRUD completo** para eventos
- **Tipos de eventos**: Conferencia, Concierto, Seminario, Taller, Reunión
- **Eventos públicos y privados**
- **Sistema de registro** de asistentes
- **Control de capacidad** y plazas disponibles
- **Filtros y búsqueda** avanzada

### Seguridad
- **Mixins de autorización** (LoginRequiredMixin, PermissionRequiredMixin)
- **Manejo de errores** y mensajes informativos
- **Middleware personalizado** para errores de permisos
- **Configuraciones de seguridad** para producción

## 📁 Estructura del Proyecto

```
event_platform/
├── event_platform/          # Configuración principal
│   ├── settings.py          # Configuraciones
│   ├── urls.py              # URLs principales
│   └── middleware/          # Middleware personalizado
├── eventos/                 # Aplicación de eventos
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Vistas CRUD
│   ├── admin.py            # Panel de administración
│   ├── urls.py             # URLs de eventos
│   └── management/         # Comandos personalizados
├── usuarios/               # Aplicación de usuarios
│   ├── views.py            # Autenticación
│   └── urls.py             # URLs de usuarios
├── templates/              # Templates HTML
│   ├── base.html           # Template base
│   ├── usuarios/           # Templates de autenticación
│   └── eventos/            # Templates de eventos
├── static/                 # Archivos estáticos
└── media/                  # Archivos multimedia
```

## 🛠️ Instalación y Configuración

### 1. Clonar y configurar el entorno

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install Django>=4.2 Pillow
```

### 2. Configurar la base de datos

```bash
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Configurar grupos y permisos
python manage.py configurar_grupos

# Crear superusuario
python manage.py createsuperuser
```

### 3. Ejecutar el servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en: http://127.0.0.1:8000/

## 👥 Sistema de Roles y Permisos

### Administradores
- ✅ **Acceso completo** al sistema
- ✅ **Crear, editar y eliminar** eventos
- ✅ **Ver eventos privados**
- ✅ **Gestionar registros** de asistentes
- ✅ **Acceso al panel admin**

### Organizadores de Eventos
- ✅ **Crear y editar** eventos propios
- ✅ **Ver eventos privados** permitidos
- ✅ **Gestionar registros** de sus eventos
- ❌ **No pueden eliminar** eventos

### Asistentes
- ✅ **Ver eventos públicos**
- ✅ **Registrarse en eventos**
- ✅ **Ver sus registros**
- ❌ **No pueden crear** eventos

## 🔍 Exploración de la Base de Datos

### Tabla `auth_permission`
El sistema utiliza la tabla auth_permission de Django que contiene:

```sql
-- Estructura de auth_permission
id (INTEGER)
name (VARCHAR)
content_type_id (INTEGER)
codename (VARCHAR)
```

### Permisos Personalizados Creados
- `can_view_private_events`: Permite ver eventos privados
- `can_manage_all_events`: Permite gestionar todos los eventos

### Estadísticas del Sistema
- **Total de permisos**: 38
- **Permisos de eventos**: 14
- **Grupos configurados**: 3
- **Tipos de eventos**: 5

## 🎨 Funcionalidades de la Interfaz

### Dashboard Principal
- **Lista de eventos** con filtros
- **Búsqueda** por título, descripción o ubicación
- **Filtros por tipo** de evento
- **Paginación** automática

### Panel de Usuario
- **Perfil** con estadísticas
- **Mis eventos** (para organizadores)
- **Acciones rápidas**
- **Información de permisos**

### Gestión de Eventos
- **Formularios intuitivos** para crear/editar
- **Validación** de fechas y capacidad
- **Subida de imágenes**
- **Estados**: Borrador, Publicado, Cancelado, Finalizado

## 🔧 Comandos Personalizados

### Configurar Grupos y Permisos
```bash
python manage.py configurar_grupos
```

Este comando:
- Crea los tipos de eventos básicos
- Configura los grupos de usuarios
- Asigna permisos específicos
- Muestra un resumen completo

## 🚨 Manejo de Errores

### Middleware de Errores
- **Captura errores de permisos** automáticamente
- **Redirige usuarios no autenticados** al login
- **Muestra mensajes informativos**
- **Página de acceso denegado** personalizada

### Mensajes del Sistema
- **Éxito**: Confirmaciones de acciones
- **Error**: Problemas y validaciones
- **Advertencia**: Situaciones importantes
- **Info**: Información adicional

## 🌐 URLs Principales

### Autenticación
- `/usuarios/login/` - Iniciar sesión
- `/usuarios/registro/` - Registro de usuario
- `/usuarios/logout/` - Cerrar sesión
- `/usuarios/perfil/` - Perfil de usuario

### Eventos
- `/eventos/` - Lista de eventos
- `/eventos/crear/` - Crear evento
- `/eventos/mis-eventos/` - Mis eventos
- `/eventos/<id>/` - Detalle del evento
- `/eventos/<id>/editar/` - Editar evento
- `/eventos/<id>/registrarse/` - Registrarse en evento

### Administración
- `/admin/` - Panel de administración Django

## 🔐 Configuraciones de Seguridad

### Configuraciones Aplicadas
```python
# Redirecciones de autenticación
LOGIN_URL = '/usuarios/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Seguridad de cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Para producción (cambiar a True con HTTPS)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```

## 📊 Casos de Uso

### Escenario 1: Organizador de Conferencias
1. **Registro** como organizador
2. **Crear evento** privado de conferencia
3. **Gestionar asistentes** registrados
4. **Modificar detalles** del evento

### Escenario 2: Asistente a Eventos
1. **Registro** como asistente
2. **Explorar eventos** públicos
3. **Registrarse** en eventos de interés
4. **Ver historial** de registros

### Escenario 3: Administrador del Sistema
1. **Acceso completo** al panel admin
2. **Gestionar todos los eventos**
3. **Asignar permisos** a usuarios
4. **Eliminar eventos** si es necesario

## 🛡️ Mejores Prácticas Implementadas

### Seguridad
- ✅ Validación de permisos en todas las vistas
- ✅ Protección CSRF activada
- ✅ Autenticación requerida para acciones sensibles
- ✅ Mensajes de error informativos sin exponer detalles técnicos

### Código
- ✅ Modelos con validaciones y métodos útiles
- ✅ Vistas basadas en clases para mejor organización
- ✅ Templates reutilizables con herencias
- ✅ Comandos de gestión personalizados

### UX/UI
- ✅ Interfaz responsive con Bootstrap
- ✅ Mensajes de feedback al usuario
- ✅ Navegación intuitiva
- ✅ Formularios con validación en tiempo real

## 🎯 Entrega Funcional Completada

### ✅ Requisitos Cumplidos

1. **Configuración del Modelo Auth de Django** ✅
   - Sistema de autenticación completo
   - Registro, login y logout funcionando

2. **Enrutamiento para Login/Logout** ✅
   - URLs configuradas correctamente
   - Redirecciones apropiadas

3. **Gestión de Roles y Permisos** ✅
   - Tres tipos de usuarios implementados
   - Permisos granulares con Django Auth

4. **Uso de Mixins en el Modelo Auth** ✅
   - LoginRequiredMixin aplicado
   - PermissionRequiredMixin en vistas sensibles

5. **Redirección de Accesos No Autorizados** ✅
   - Vista de acceso denegado
   - Mensajes de error informativos

6. **Manejo de Errores y Mensajes** ✅
   - Sistema de mensajes implementado
   - Middleware de manejo de errores

7. **Ejecutando las Migraciones** ✅
   - Base de datos configurada
   - Tablas creadas correctamente

8. **Exploración de la Tabla auth_permission** ✅
   - Análisis completo realizado
   - Permisos asignados correctamente

9. **Configuración de Seguridad** ✅
   - Settings de seguridad aplicados
   - Preparado para HTTPS en producción

---

## 🏆 Resultado Final

**Plataforma completamente funcional** con:
- Sistema de autenticación robusto
- Gestión completa de eventos
- Roles y permisos granulares
- Interfaz de usuario intuitiva
- Configuraciones de seguridad aplicadas

**¡Lista para usar y desplegar en producción!** 🚀