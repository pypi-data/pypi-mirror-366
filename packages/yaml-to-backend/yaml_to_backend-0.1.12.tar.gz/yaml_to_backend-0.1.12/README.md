# YAML-to-Backend

Una librería Python para generar backends completos a partir de definiciones YAML.

## ¿Qué es YAML-to-Backend?

YAML-to-Backend es una herramienta que permite generar automáticamente backends completos con FastAPI, SQLAlchemy y SQLModel a partir de archivos YAML que definen entidades, campos, relaciones y permisos. Es ideal para startups y desarrolladores que necesitan prototipar rápidamente APIs RESTful sin escribir código repetitivo.

### Características Principales

- **Generación automática de modelos**: Crea modelos SQLModel y Pydantic automáticamente
- **CRUD automático**: Genera endpoints CRUD completos para cada entidad
- **Autenticación integrada**: Sistema de autenticación JWT incluido
- **Validación automática**: Validación de datos basada en las definiciones YAML
- **Documentación automática**: Swagger/OpenAPI generado automáticamente
- **Soporte para relaciones**: Claves foráneas y relaciones entre entidades
- **Sistema de permisos**: Control de acceso basado en roles con soporte "yo"
- **Borrado lógico**: Soporte para soft delete configurable

## Instalación

```bash
pip install yaml-to-backend
```

## Uso Rápido

### 1. Definir entidades en YAML

Crea archivos YAML que definan tus entidades:

```yaml
# entidades/usuario.yaml
entidad: Usuario
tabla: usuarios
descripcion: Gestión de usuarios del sistema
campos:
  id:
    tipo: integer
    pk: true
  nombre:
    tipo: string
    max: 100
    required: true
    ejemplo: "Juan Pérez"
  email:
    tipo: string
    max: 255
    required: true
    ejemplo: "juan@ejemplo.com"
  password:
    tipo: string
    max: 255
    required: true
  rol:
    tipo: string
    max: 50
    required: true
    ejemplo: "admin"
  habilitado:
    tipo: boolean
    required: true
    ejemplo: true
permisos:
  admin: [r, w, d]
  usuario:
    yo:
      campo_usuario: id
```

### 2. Configurar y ejecutar

```python
from yaml_to_backend import update_config, get_run_backend

# Configurar la base de datos
update_config(
    ENTITIES_PATH='./entidades/',
    DB_HOST='localhost',
    DB_USER='usuario',
    DB_PASSWORD='password',
    DB_NAME='mi_base_datos',
    DB_PORT=3306,
    PORT=8000,
    INSTALL=True,  # Recrear base de datos
    AUTH={
        'tabla': 'usuarios',
        'columna_usuario': 'nombre',
        'columna_password': 'password',
        'superusuario': 'admin',
        'password_default': 'admin123',
        'columna_borrado': 'habilitado',
        'borrado_logico': 'boolean'
    },
    INITIAL_USERS=[
        {'nombre': 'admin', 'password': 'admin123', 'rol': 'admin', 'habilitado': True},
        {'nombre': 'usuario1', 'password': 'user123', 'rol': 'usuario', 'habilitado': True}
    ]
)

# Ejecutar el backend
run_backend = get_run_backend()
run_backend()
```

### 3. Usar desde línea de comandos

```bash
# Configurar y ejecutar
yaml-to-backend --config entidades/ --port 8000

# Solo validar YAML
yaml-to-backend --validate entidades/
```

## Ejemplos Completos de Configuración

### Configuración Básica

```python
from yaml_to_backend import update_config, get_run_backend

update_config(
    ENTITIES_PATH='./entidades/',
    DB_HOST='localhost',
    DB_USER='root',
    DB_PASSWORD='1234',
    DB_NAME='mi_base',
    DB_PORT=3306,
    PORT=8000,
    INSTALL=True,
    DEBUG=True,
    LOG=True
)
```

### Configuración Avanzada con Autenticación

```python
update_config(
    ENTITIES_PATH='./entidades/',
    DB_HOST='100.123.161.101',
    DB_USER='root',
    DB_PASSWORD='1234',
    DB_NAME='mi_base',
    DB_PORT=3306,
    PORT=8007,
    INSTALL=True,
    DEBUG=True,
    LOG=True,
    AUTH={
        'tabla': 'usuarios',
        'columna_usuario': 'nombre',
        'columna_password': 'password',
        'superusuario': 'admin',
        'password_default': 'admin123',
        'columna_borrado': 'habilitado',
        'borrado_logico': 'boolean'
    },
    INITIAL_USERS=[
        {'nombre': 'admin', 'password': 'admin123', 'rol': 'admin', 'habilitado': True, 'email': 'admin@ejemplo.com'},
        {'nombre': 'estudiante', 'password': 'estudiante123', 'rol': 'usuario', 'habilitado': True, 'email': 'estudiante@ejemplo.com'},
        {'nombre': 'desarrollador', 'password': 'dev123', 'rol': 'admin', 'habilitado': True, 'email': 'dev@ejemplo.com'}
    ]
)
```

## Ejemplos de Archivos YAML

### Entidad Simple (Roles)

```yaml
# entidades/roles.yaml
entidad: Roles
tabla: roles
descripcion: Roles de usuarios del sistema
campos:
  id:
    tipo: integer
    pk: true
  rol:
    tipo: string
    max: 50
    required: true
    ejemplo: "admin"
permisos:
  admin: [r, w, d]
```

### Entidad con Relaciones (Contenedores)

```yaml
# entidades/contenedores.yaml
entidad: Contenedores
tabla: contenedores
descripcion: Gestión de contenedores de usuarios
campos:
  id:
    tipo: integer
    pk: true
  nombre:
    tipo: string
    max: 100
    required: true
    ejemplo: "mi-aplicacion-web"
  http:
    tipo: integer
    required: false
    ejemplo: 8080
  https:
    tipo: integer
    required: false
    ejemplo: 8443
  puertos:
    tipo: text
    required: false
    ejemplo: "8080:80,8443:443"
  redes:
    tipo: text
    required: false
    ejemplo: "bridge,host"
  variables:
    tipo: text
    required: false
    ejemplo: "DB_HOST=localhost,DB_PORT=3306"
  volumenes:
    tipo: text
    required: false
    ejemplo: "/host/data:/container/data"
  imagen:
    tipo: integer
    fk: imagenes.id
    required: true
  usuario:
    tipo: integer
    fk: usuarios.id
    required: true
permisos:
  admin: [r, w, d]
  usuario:
    yo:
      campo_usuario: usuario
```

### Entidad Compleja (Perfiles)

```yaml
# entidades/perfiles.yaml
entidad: Perfiles
tabla: perfiles
descripcion: Perfiles de usuario con información personal
campos:
  id:
    tipo: integer
    pk: true
  nombre:
    tipo: string
    max: 100
    required: true
    ejemplo: "Juan"
  apellido:
    tipo: string
    max: 100
    required: true
    ejemplo: "Pérez"
  email:
    tipo: string
    max: 255
    required: true
    ejemplo: "juan.perez@test.com"
  imagen:
    tipo: text
    required: false
    ejemplo: "https://example.com/avatar.jpg"
  telefono:
    tipo: string
    max: 20
    required: false
    ejemplo: "+1234567890"
  fecha_nacimiento:
    tipo: date
    required: false
    ejemplo: "1990-01-01"
  usuario:
    tipo: integer
    fk: usuarios.id
    required: true
permisos:
  admin: [r, w, d]
  usuario:
    yo:
      campo_usuario: usuario
```

## Tipos de Datos Soportados

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `integer` | Números enteros | `123` |
| `string` | Cadenas de texto | `"Hola mundo"` |
| `boolean` | Valores booleanos | `true`, `false` |
| `datetime` | Fechas y horas | `"2023-12-31T23:59:59"` |
| `date` | Solo fechas | `"2023-12-31"` |
| `time` | Solo horas | `"23:59:59"` |
| `float` | Números decimales | `3.14159` |
| `text` | Texto largo | `"Texto muy largo..."` |
| `json` | Datos JSON | `{"key": "value"}` |

## Ejemplos de Uso de Endpoints

### Autenticación

```bash
# Login
curl -X POST "http://localhost:8007/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Obtener información del usuario actual
curl -X GET "http://localhost:8007/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Operaciones CRUD

```bash
# Crear un nuevo rol
curl -X POST "http://localhost:8007/api/roles/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"rol":"desarrollador"}'

# Obtener todos los roles
curl -X GET "http://localhost:8007/api/roles/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Obtener un rol específico
curl -X GET "http://localhost:8007/api/roles/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Actualizar un rol
curl -X PUT "http://localhost:8007/api/roles/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"rol":"admin"}'

# Eliminar un rol
curl -X DELETE "http://localhost:8007/api/roles/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Operaciones con Relaciones

```bash
# Crear un contenedor (requiere imagen y usuario existentes)
curl -X POST "http://localhost:8007/api/contenedores/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "nombre":"mi-aplicacion-web",
    "http":8080,
    "https":8443,
    "puertos":"8080:80,8443:443",
    "redes":"bridge,host",
    "variables":"DB_HOST=localhost,DB_PORT=3306",
    "volumenes":"/host/data:/container/data",
    "imagen":1,
    "usuario":1
  }'
```

## Uso de Modelos ORM Generados

### Acceso Directo a Modelos

```python
from yaml_to_backend.db.generated_models import Roles, Usuario, Contenedores
from sqlmodel import select
from yaml_to_backend.db.connection import get_session

# Obtener sesión de base de datos
async with get_session() as session:
    # Crear un nuevo rol
    nuevo_rol = Roles(rol="desarrollador")
    session.add(nuevo_rol)
    await session.commit()
    
    # Consultar roles
    statement = select(Roles)
    roles = await session.exec(statement).all()
    
    # Filtrar por rol
    statement = select(Roles).where(Roles.rol == "admin")
    admin_roles = await session.exec(statement).all()
    
    # Obtener con relaciones
    statement = select(Contenedores).where(Contenedores.usuario == 1)
    contenedores_usuario = await session.exec(statement).all()
```

### Uso de Modelos Pydantic

#### Acceso Directo a Modelos

```python
from yaml_to_backend.db.generated_models import RolesCreate, RolesResponse, RolesUpdate

# Crear datos para nuevo rol
datos_crear = RolesCreate(rol="desarrollador")

# Datos para actualización
datos_actualizar = RolesUpdate(rol="admin")

# Respuesta del modelo
rol_respuesta = RolesResponse(id=1, rol="admin")
```

#### Diccionario Centralizado PYDANTIC_MODELS

La librería proporciona un diccionario centralizado con todos los modelos Pydantic generados:

```python
from yaml_to_backend.db.generated_models import (
    PYDANTIC_MODELS,
    get_pydantic_model,
    get_all_entities,
    get_entity_actions,
    validate_entity_action
)

# Acceso directo al diccionario
usuario_create = PYDANTIC_MODELS["Usuario"]["create"]
usuario_update = PYDANTIC_MODELS["Usuario"]["update"]
usuario_response = PYDANTIC_MODELS["Usuario"]["response"]

# Usar funciones utilitarias
try:
    # Obtener modelo de creación para Usuario
    UsuarioCreate = get_pydantic_model("Usuario", "create")
    
    # Crear datos validados
    datos_usuario = UsuarioCreate(
        nombre="Juan Pérez",
        email="juan@ejemplo.com",
        password="password123",
        rol="usuario"
    )
    
    # Validar datos
    datos_validados = datos_usuario.model_dump()
    print(datos_validados)
    
except KeyError as e:
    print(f"Error: {e}")

# Listar todas las entidades disponibles
print("Entidades disponibles:", get_all_entities())

# Obtener acciones de una entidad
actions = get_entity_actions("Usuario")  # ["create", "update", "response"]

# Validar si existe un modelo
exists = validate_entity_action("Usuario", "create")  # True
```

#### Casos de Uso Avanzados

```python
# Validación dinámica de datos
def validate_data(entity_name: str, action: str, data: dict):
    if validate_entity_action(entity_name, action):
        model_class = get_pydantic_model(entity_name, action)
        return model_class(**data)
    else:
        raise ValueError(f"Modelo no disponible: {entity_name}.{action}")

# Generación de formularios dinámicos
def get_form_fields(entity_name: str):
    create_model = get_pydantic_model(entity_name, "create")
    return create_model.model_fields

# Serialización de respuestas
def serialize_response(entity_name: str, data: dict):
    response_model = get_pydantic_model(entity_name, "response")
    return response_model(**data)

# Ejemplo de uso
try:
    # Validar datos de entrada
    datos_validados = validate_data("Usuario", "create", {
        "nombre": "Ana García",
        "email": "ana@ejemplo.com",
        "password": "password123",
        "rol": "usuario"
    })
    
    # Obtener campos del formulario
    campos = get_form_fields("Usuario")
    print("Campos requeridos:", [campo for campo, info in campos.items() if info.is_required])
    
except Exception as e:
    print(f"Error: {e}")
```

## Sistema de Permisos

### Tipos de Permisos

- `r`: Read (lectura)
- `w`: Write (escritura)
- `d`: Delete (eliminación)

### Configuración de Permisos

```yaml
permisos:
  admin: [r, w, d]  # Admin tiene todos los permisos
  usuario:
    yo:  # Usuario solo puede acceder a sus propios registros
      campo_usuario: id  # Campo que identifica al usuario
  moderador: [r, w]  # Moderador puede leer y escribir, pero no eliminar
```

### Permisos "Yo"

El sistema de permisos "yo" permite que los usuarios solo accedan a registros donde el campo especificado coincida con su ID de usuario:

```yaml
# Usuario solo puede ver/editar contenedores donde usuario = su_id
permisos:
  usuario:
    yo:
      campo_usuario: usuario
```

## Documentación de Clases y Métodos

### EntityParser

**Ubicación**: `yaml_to_backend.core.entity_parser`

**Descripción**: Clase responsable de cargar y parsear archivos YAML de entidades.

#### Métodos

- `__init__(entities_path: str)`: Inicializa el parser con la ruta de entidades
- `load_entities() -> Dict[str, Any]`: Carga todas las entidades desde archivos YAML
- `get_entity(entity_name: str) -> Optional[Dict[str, Any]]`: Obtiene una entidad específica
- `get_all_entities() -> Dict[str, Any]`: Obtiene todas las entidades cargadas
- `validate_entity(entity_data: Dict[str, Any]) -> bool`: Valida la estructura de una entidad

### ModelGenerator

**Ubicación**: `yaml_to_backend.core.model_generator`

**Descripción**: Genera modelos SQLModel y Pydantic a partir de definiciones YAML.

#### Métodos

- `__init__()`: Inicializa el generador de modelos
- `generate_model_code(entity_name: str, entity_data: Dict[str, Any]) -> str`: Genera código Python para un modelo SQLModel
- `generate_pydantic_models_code(entity_name: str, entity_data: Dict[str, Any]) -> str`: Genera modelos Pydantic (Create, Response, Update)
- `generate_swagger_documentation(entity_name: str, entity_data: Dict[str, Any]) -> Dict[str, Any]`: Genera documentación Swagger
- `write_models_file(entities: Dict[str, Any])`: Escribe los modelos generados a archivo
- `write_base_models_file(entities: Dict[str, Any])`: Escribe archivo base de modelos
- `import_generated_models()`: Importa los modelos generados dinámicamente
- `generate_all_models(entities: Dict[str, Any]) -> Dict[str, Any]`: Genera todos los modelos

### AuthManager

**Ubicación**: `yaml_to_backend.security.auth`

**Descripción**: Maneja autenticación, autorización y gestión de tokens JWT.

#### Métodos

- `__init__()`: Inicializa el gestor de autenticación
- `verify_password(plain_password: str, hashed_password: str) -> bool`: Verifica contraseñas
- `get_password_hash(password: str) -> str`: Genera hash de contraseña
- `create_access_token(data: dict) -> str`: Crea token JWT
- `verify_token(token: str) -> Optional[dict]`: Verifica token JWT
- `authenticate_user(username: str, password: str, session) -> Optional[Any]`: Autentica usuario
- `get_current_user(credentials: HTTPAuthorizationCredentials, session) -> Any`: Obtiene usuario actual
- `has_permission(user: Any, entity_permissions: Dict[str, Any], action: str) -> bool`: Verifica permisos

### DatabaseManager

**Ubicación**: `yaml_to_backend.db.connection`

**Descripción**: Gestiona conexiones y sesiones de base de datos.

#### Métodos

- `__init__()`: Inicializa el gestor de base de datos
- `get_engine()`: Obtiene el motor de base de datos
- `get_session()`: Obtiene sesión de base de datos
- `create_tables()`: Crea todas las tablas
- `drop_tables()`: Elimina todas las tablas
- `reset_database()`: Reinicia la base de datos

### BackendGenerator

**Ubicación**: `yaml_to_backend.app`

**Descripción**: Clase principal que orquesta la generación del backend completo.

#### Métodos

- `__init__()`: Inicializa el generador de backend
- `load_entities()`: Carga entidades desde archivos YAML
- `generate_models()`: Genera modelos ORM y Pydantic
- `initialize_database()`: Inicializa la base de datos
- `create_initial_users()`: Crea usuarios iniciales
- `generate_crud_routes()`: Genera rutas CRUD
- `create_app()`: Crea la aplicación FastAPI
- `run()`: Ejecuta el servidor

## Dependencias y Librerías Utilizadas

### Dependencias Principales

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `fastapi` | >=0.104.0 | Framework web para APIs REST |
| `uvicorn[standard]` | >=0.24.0 | Servidor ASGI para FastAPI |
| `sqlalchemy` | >=2.0.0 | ORM para base de datos |
| `sqlmodel` | >=0.0.8 | Integración SQLAlchemy + Pydantic |
| `pydantic` | >=2.0.0 | Validación de datos y serialización |
| `pyyaml` | >=6.0 | Parsing de archivos YAML |
| `bcrypt` | >=4.0.0 | Hashing de contraseñas |
| `python-jose[cryptography]` | >=3.3.0 | Manejo de tokens JWT |
| `python-multipart` | >=0.0.6 | Manejo de formularios multipart |
| `asyncmy` | >=0.2.8 | Driver MySQL asíncrono |
| `python-dotenv` | >=1.0.0 | Carga de variables de entorno |
| `inflection` | >=0.5.0 | Pluralización y transformación de strings |
| `passlib[bcrypt]` | >=1.7.0 | Utilidades de hashing de contraseñas |

### Dependencias de Desarrollo

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `pytest` | >=7.0.0 | Framework de testing |
| `pytest-asyncio` | >=0.21.0 | Soporte async para pytest |
| `httpx` | >=0.24.0 | Cliente HTTP para testing |
| `black` | >=23.0.0 | Formateador de código |
| `flake8` | >=6.0.0 | Linter de código |

### Análisis de Uso de Dependencias

Todas las dependencias listadas están siendo utilizadas activamente:

- **FastAPI + Uvicorn**: Core del servidor web
- **SQLAlchemy + SQLModel**: ORM y modelos de datos
- **Pydantic**: Validación y serialización
- **PyYAML**: Parsing de archivos de configuración
- **bcrypt + passlib**: Seguridad y hashing
- **python-jose**: Tokens JWT
- **asyncmy**: Conexión MySQL asíncrona
- **python-dotenv**: Configuración
- **inflection**: Transformación de nombres de entidades
- **python-multipart**: Manejo de formularios

## Estructura del Proyecto

```
yaml-to-backend/
├── yaml_to_backend/          # Código fuente de la librería
│   ├── __init__.py
│   ├── app.py               # Aplicación principal
│   ├── config.py            # Configuración
│   ├── cli.py               # Interfaz de línea de comandos
│   ├── api/                 # Generadores de API
│   │   ├── __init__.py
│   │   ├── auth_routes.py   # Rutas de autenticación
│   │   └── crud_generator.py # Generador de CRUD
│   ├── core/                # Lógica principal
│   │   ├── __init__.py
│   │   ├── entity_parser.py # Parser de YAML
│   │   └── model_generator.py # Generador de modelos
│   ├── db/                  # Base de datos
│   │   ├── __init__.py
│   │   └── connection.py    # Gestión de conexiones
│   └── security/            # Autenticación y seguridad
│       ├── __init__.py
│       └── auth.py          # Gestor de autenticación
├── tests/                   # Pruebas y ejemplos
│   ├── entidades/           # Archivos YAML de ejemplo
│   ├── main.py              # Script de prueba
│   ├── pruebas_curl.sh      # Pruebas de endpoints
│   └── ORM Tests/           # Pruebas de modelos ORM
├── pyproject.toml           # Configuración del proyecto
├── MANIFEST.in              # Archivos del paquete
└── README.md                # Este archivo
```

## Configuración Avanzada

### Variables de Entorno

```bash
# Base de datos
DB_HOST=localhost
DB_USER=usuario
DB_PASSWORD=password
DB_NAME=mi_base_datos
DB_PORT=3306

# Servidor
PORT=8000
SECRET_KEY=mi_clave_secreta_muy_larga
ALGORITHM=HS256

# Configuración
ENTITIES_PATH=./entidades/
INSTALL=false
DEBUG=true
LOG=true
```

### Configuración de Autenticación

```python
AUTH = {
    'tabla': 'usuarios',           # Tabla de usuarios
    'columna_usuario': 'nombre',   # Columna para username
    'columna_password': 'password', # Columna para password
    'superusuario': 'admin',       # Usuario con permisos totales
    'password_default': 'admin123', # Password por defecto
    'columna_borrado': 'habilitado', # Columna para soft delete
    'borrado_logico': 'boolean'    # Tipo de borrado lógico
}
```

## Desarrollo

### Instalación para desarrollo

```bash
git clone https://github.com/cxmjg/yaml-to-backend.git
cd yaml-to-backend
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -e .
```

### Ejecutar pruebas

```bash
# Pruebas de endpoints
cd tests
./pruebas_curl.sh

# Pruebas de modelos ORM
pytest "ORM Tests/"
```

### Construir el paquete

```bash
python -m build
```

## Publicación Automática

Este proyecto utiliza GitHub Actions con Trusted Publishers para publicar automáticamente en PyPI cuando se hace push a la rama `main`.

### Configuración de Trusted Publishers

1. Ve a tu proyecto en PyPI
2. En "Settings" > "Trusted publishers"
3. Agrega un nuevo publisher con:
   - **Owner**: `cxmjg`
   - **Repository name**: `yaml-to-backend`
   - **Workflow name**: `publish`
   - **Environment name**: (dejar vacío)

## Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Changelog

### v0.1.12
- Agregar soporte oficial para Python 3.13
- Documentación completa del diccionario PYDANTIC_MODELS
- Crear README_IA para contexto completo de IA
- Mejoras en ejemplos de uso y casos de uso avanzados
- Verificación de compatibilidad con última versión de Python

### v0.1.11
- Corrección de problemas de autenticación
- Mejora en el manejo de eventos asíncronos
- Actualización de dependencias
- Mejoras en la documentación

### v0.1.10
- Corrección de problemas de autenticación
- Mejora en el manejo de eventos asíncronos
- Actualización de dependencias
- Mejoras en la documentación

### v0.1.9
- Corrección de configuración de autenticación
- Mejora en la creación de usuarios iniciales
- Actualización de ejemplos

### v0.1.8
- Primera versión estable
- Generación automática de modelos y CRUD
- Sistema de autenticación JWT
- Soporte para relaciones entre entidades
- CLI para configuración y validación
- Publicación automática con GitHub Actions 