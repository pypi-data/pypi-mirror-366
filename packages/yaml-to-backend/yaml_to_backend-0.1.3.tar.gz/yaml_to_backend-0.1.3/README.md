# YAML-to-Backend

Una librería Python para generar backends completos a partir de definiciones YAML.

## Descripción

YAML-to-Backend es una herramienta que permite generar automáticamente backends completos con FastAPI, SQLAlchemy y SQLModel a partir de archivos YAML que definen entidades, campos, relaciones y permisos.

## Características

- **Generación automática de modelos**: Crea modelos SQLModel y Pydantic automáticamente
- **CRUD automático**: Genera endpoints CRUD completos para cada entidad
- **Autenticación integrada**: Sistema de autenticación JWT incluido
- **Validación automática**: Validación de datos basada en las definiciones YAML
- **Documentación automática**: Swagger/OpenAPI generado automáticamente
- **Soporte para relaciones**: Claves foráneas y relaciones entre entidades
- **Sistema de permisos**: Control de acceso basado en roles

## Instalación

```bash
pip install yaml-to-backend
```

## Uso

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
  email:
    tipo: string
    max: 255
    required: true
    ejemplo: "usuario@ejemplo.com"
  password:
    tipo: string
    max: 255
    required: true
  activo:
    tipo: boolean
    required: true
    ejemplo: true
  rol_id:
    tipo: integer
    fk: roles.id
    required: true
permisos:
  admin: [r, w, d]
  usuario:
    yo:
      campo_usuario: id
```

### 2. Usar la librería

```python
from yaml_to_backend import update_config, get_run_backend

# Configurar la base de datos
update_config(
    DB_HOST='localhost',
    DB_USER='usuario',
    DB_PASSWORD='password',
    DB_NAME='mi_base_datos',
    DB_PORT=3306,
    PORT=8000
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

## Estructura del Proyecto

```
yaml-to-backend/
├── yaml_to_backend/          # Código fuente de la librería
│   ├── __init__.py
│   ├── app.py               # Aplicación principal
│   ├── config.py            # Configuración
│   ├── cli.py               # Interfaz de línea de comandos
│   ├── api/                 # Generadores de API
│   ├── core/                # Lógica principal
│   ├── db/                  # Modelos de base de datos
│   └── security/            # Autenticación y seguridad
├── tests/                   # Pruebas unitarias
├── setup.py                 # Configuración de instalación
├── pyproject.toml           # Configuración moderna del proyecto
├── MANIFEST.in              # Archivos a incluir en el paquete
└── README.md                # Este archivo
```

## Tipos de Datos Soportados

- `integer`: Números enteros
- `string`: Cadenas de texto
- `boolean`: Valores booleanos
- `datetime`: Fechas y horas
- `date`: Solo fechas
- `time`: Solo horas
- `float`: Números decimales
- `text`: Texto largo
- `json`: Datos JSON

## Configuración

### Variables de Entorno

- `DB_HOST`: Host de la base de datos
- `DB_USER`: Usuario de la base de datos
- `DB_PASSWORD`: Contraseña de la base de datos
- `DB_NAME`: Nombre de la base de datos
- `DB_PORT`: Puerto de la base de datos
- `PORT`: Puerto del servidor web
- `SECRET_KEY`: Clave secreta para JWT
- `ALGORITHM`: Algoritmo de encriptación JWT

### Configuración Programática

```python
from yaml_to_backend import update_config

update_config(
    DB_HOST='localhost',
    DB_USER='usuario',
    DB_PASSWORD='password',
    DB_NAME='mi_db',
    DB_PORT=3306,
    PORT=8000,
    SECRET_KEY='mi_clave_secreta',
    ALGORITHM='HS256'
)
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
pytest
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

### v0.1.0
- Primera versión estable
- Generación automática de modelos y CRUD
- Sistema de autenticación JWT
- Soporte para relaciones entre entidades
- CLI para configuración y validación
- Publicación automática con GitHub Actions 