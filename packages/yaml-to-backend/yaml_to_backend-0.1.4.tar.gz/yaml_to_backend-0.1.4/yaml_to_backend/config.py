import os
from typing import Dict, Any

# =============================================================================
# CONFIGURACIÓN POR DEFECTO
# =============================================================================

# Configuración de rutas
DEFAULT_ENTITIES_PATH = './entidades/'

# Configuración de base de datos
DEFAULT_DB_HOST = 'localhost'
DEFAULT_DB_PORT = 3306
DEFAULT_DB_USER = 'root'
DEFAULT_DB_PASSWORD = '1234'
DEFAULT_DB_NAME = 'mi_base'

# Configuración del servidor
DEFAULT_DEBUG = True
DEFAULT_PORT = 8000
DEFAULT_INSTALL = True
DEFAULT_LOG = True

# Configuración de autenticación
DEFAULT_AUTH = {
    'tabla': 'usuarios',
    'columna_usuario': 'username',
    'columna_password': 'password',
    'superusuario': 'admin',
    'password_default': 'admin123',
    'columna_borrado': 'deleted_at',
    'borrado_logico': 'timestamp'
}

# Configuración JWT
DEFAULT_JWT_SECRET_KEY = 'tu_clave_secreta_muy_segura_aqui'
DEFAULT_JWT_ALGORITHM = "HS256"
DEFAULT_JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de usuarios iniciales para modo instalación
DEFAULT_INITIAL_USERS = [
    {
        'username': 'admin',
        'password': 'admin123',
        'rol': 'admin'
    },
    {
        'username': 'usuario1',
        'password': 'usuario123',
        'rol': 'usuario'
    }
]

# =============================================================================
# VARIABLES DE CONFIGURACIÓN (se pueden sobrescribir)
# =============================================================================

# Configuración de rutas
ENTITIES_PATH = os.getenv('ENTITIES_PATH', DEFAULT_ENTITIES_PATH)

# Configuración de base de datos
DB_HOST = os.getenv('DB_HOST', DEFAULT_DB_HOST)
DB_PORT = int(os.getenv('DB_PORT', DEFAULT_DB_PORT))
DB_USER = os.getenv('DB_USER', DEFAULT_DB_USER)
DB_PASSWORD = os.getenv('DB_PASSWORD', DEFAULT_DB_PASSWORD)
DB_NAME = os.getenv('DB_NAME', DEFAULT_DB_NAME)

# Configuración del servidor
DEBUG = os.getenv('DEBUG', str(DEFAULT_DEBUG)).lower() == 'true'
PORT = int(os.getenv('PORT', DEFAULT_PORT))
INSTALL = os.getenv('INSTALL', str(DEFAULT_INSTALL)).lower() == 'true'
LOG = os.getenv('LOG', str(DEFAULT_LOG)).lower() == 'true'

# Configuración de autenticación
AUTH = DEFAULT_AUTH.copy()

# Configuración JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', DEFAULT_JWT_SECRET_KEY)
JWT_ALGORITHM = DEFAULT_JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = DEFAULT_JWT_ACCESS_TOKEN_EXPIRE_MINUTES

# URL de conexión a la base de datos
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuración de usuarios iniciales para modo instalación
INITIAL_USERS = DEFAULT_INITIAL_USERS.copy()

# =============================================================================
# FUNCIÓN PARA SOBRESCRIBIR CONFIGURACIÓN
# =============================================================================

def update_config(**kwargs):
    """
    Permite sobrescribir valores de configuración por defecto.
    
    Args:
        **kwargs: Pares clave-valor con la configuración a sobrescribir
        
    Ejemplo:
        update_config(
            PORT=8002,
            DB_HOST='localhost',
            DEBUG=False,
            INITIAL_USERS=[{'username': 'admin', 'password': 'admin123', 'rol': 'admin'}]
        )
    """
    global ENTITIES_PATH, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    global DEBUG, PORT, INSTALL, LOG, AUTH, JWT_SECRET_KEY, JWT_ALGORITHM
    global JWT_ACCESS_TOKEN_EXPIRE_MINUTES, DATABASE_URL, INITIAL_USERS
    
    # Actualizar variables individuales
    if 'ENTITIES_PATH' in kwargs:
        ENTITIES_PATH = kwargs['ENTITIES_PATH']
    
    if 'DB_HOST' in kwargs:
        DB_HOST = kwargs['DB_HOST']
    
    if 'DB_PORT' in kwargs:
        DB_PORT = int(kwargs['DB_PORT'])
    
    if 'DB_USER' in kwargs:
        DB_USER = kwargs['DB_USER']
    
    if 'DB_PASSWORD' in kwargs:
        DB_PASSWORD = kwargs['DB_PASSWORD']
    
    if 'DB_NAME' in kwargs:
        DB_NAME = kwargs['DB_NAME']
    
    if 'DEBUG' in kwargs:
        DEBUG = kwargs['DEBUG']
    
    if 'PORT' in kwargs:
        PORT = int(kwargs['PORT'])
    
    if 'INSTALL' in kwargs:
        INSTALL = kwargs['INSTALL']
    
    if 'LOG' in kwargs:
        LOG = kwargs['LOG']
    
    if 'AUTH' in kwargs:
        AUTH = kwargs['AUTH'].copy()
    
    if 'JWT_SECRET_KEY' in kwargs:
        JWT_SECRET_KEY = kwargs['JWT_SECRET_KEY']
    
    if 'JWT_ALGORITHM' in kwargs:
        JWT_ALGORITHM = kwargs['JWT_ALGORITHM']
    
    if 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES' in kwargs:
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES = kwargs['JWT_ACCESS_TOKEN_EXPIRE_MINUTES']
    
    if 'INITIAL_USERS' in kwargs:
        INITIAL_USERS = kwargs['INITIAL_USERS'].copy()
    
    # Recalcular DATABASE_URL si se modificó alguna configuración de BD
    if any(key in kwargs for key in ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']):
        DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" 