"""Modelos generados automáticamente desde entidades YAML"""

from typing import Optional, Dict, Type, Any
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from datetime import datetime

# Importar modelos existentes
from .models import Usuario, Tarea, Categoria, Articulo


class UsuarioCreate(BaseModel):
    """Modelo para crear Usuario - Gestión de usuarios del sistema"""
    username: str
    password: str
    rol: str

class UsuarioUpdate(BaseModel):
    """Modelo para actualizar Usuario"""
    username: Optional[str]
    password: Optional[str]
    rol: Optional[str]

class UsuarioResponse(BaseModel):
    """Modelo para respuesta de Usuario"""
    id: int
    username: str
    password: str
    rol: str
    deleted_at: Optional[datetime]

class TareaCreate(BaseModel):
    """Modelo para crear Tarea - Gestión de tareas del sistema"""
    titulo: str
    descripcion: str
    usuario_id: int
    completada: bool

class TareaUpdate(BaseModel):
    """Modelo para actualizar Tarea"""
    titulo: Optional[str]
    descripcion: Optional[str]
    completada: Optional[bool]

class TareaResponse(BaseModel):
    """Modelo para respuesta de Tarea"""
    id: int
    titulo: str
    descripcion: str
    usuario_id: int
    completada: bool
    fecha_creacion: Optional[datetime]
    deleted_at: Optional[datetime]

class CategoriaCreate(BaseModel):
    """Modelo para crear Categoria - Gestión de categoria"""
    nombre: str
    descripcion: str
    color: str
    activa: bool
    orden: int

class CategoriaUpdate(BaseModel):
    """Modelo para actualizar Categoria"""
    nombre: Optional[str]
    descripcion: Optional[str]
    color: Optional[str]
    activa: Optional[bool]
    orden: Optional[int]

class CategoriaResponse(BaseModel):
    """Modelo para respuesta de Categoria"""
    id: int
    nombre: str
    descripcion: str
    color: str
    activa: bool
    orden: int
    deleted_at: Optional[datetime]

class ArticuloCreate(BaseModel):
    """Modelo para crear Articulo - Gestión de articulos"""
    titulo: str
    contenido: str
    autor_id: int
    publicado: bool
    fecha_publicacion: datetime
    tags: str

class ArticuloUpdate(BaseModel):
    """Modelo para actualizar Articulo"""
    titulo: Optional[str]
    contenido: Optional[str]
    publicado: Optional[bool]
    fecha_publicacion: Optional[datetime]
    tags: Optional[str]

class ArticuloResponse(BaseModel):
    """Modelo para respuesta de Articulo"""
    id: int
    titulo: str
    contenido: str
    autor_id: int
    publicado: bool
    fecha_publicacion: datetime
    tags: str
    deleted_at: Optional[datetime]



# =============================================================================
# DICCIONARIO CENTRALIZADO DE MODELOS PYDANTIC
# =============================================================================
# Este diccionario facilita el acceso programático a todos los modelos generados
# Estructura: {entidad: {accion: clase_modelo}}

PYDANTIC_MODELS: Dict[str, Dict[str, Type[BaseModel]]] = {
    "Usuario": {
        "create": UsuarioCreate,
        "update": UsuarioUpdate,
        "response": UsuarioResponse
    },
    "Tarea": {
        "create": TareaCreate,
        "update": TareaUpdate,
        "response": TareaResponse
    },
    "Categoria": {
        "create": CategoriaCreate,
        "update": CategoriaUpdate,
        "response": CategoriaResponse
    },
    "Articulo": {
        "create": ArticuloCreate,
        "update": ArticuloUpdate,
        "response": ArticuloResponse
    },
}

# =============================================================================
# FUNCIONES UTILITARIAS PARA ACCESO A MODELOS
# =============================================================================

def get_pydantic_model(entity_name: str, action: str) -> Type[BaseModel]:
    """
    Obtiene un modelo Pydantic específico por entidad y acción.
    
    Args:
        entity_name: Nombre de la entidad (ej: "Usuario", "Tarea")
        action: Acción del modelo ("create", "update", "response")
    
    Returns:
        Clase del modelo Pydantic solicitado
        
    Raises:
        KeyError: Si la entidad o acción no existe
    """
    try:
        return PYDANTIC_MODELS[entity_name][action]
    except KeyError:
        available_entities = list(PYDANTIC_MODELS.keys())
        available_actions = list(PYDANTIC_MODELS.get(entity_name, {}).keys())
        raise KeyError(
            f"Modelo no encontrado para entidad '{entity_name}' y acción '{action}'. "
            f"Entidades disponibles: {available_entities}. "
            f"Acciones disponibles para '{entity_name}': {available_actions}"
        )

def get_all_entities() -> list[str]:
    """Obtiene la lista de todas las entidades disponibles."""
    return list(PYDANTIC_MODELS.keys())

def get_entity_actions(entity_name: str) -> list[str]:
    """Obtiene las acciones disponibles para una entidad específica."""
    if entity_name not in PYDANTIC_MODELS:
        raise KeyError(f"Entidad '{entity_name}' no encontrada")
    return list(PYDANTIC_MODELS[entity_name].keys())

def validate_entity_action(entity_name: str, action: str) -> bool:
    """Valida si existe un modelo para la entidad y acción especificadas."""
    return entity_name in PYDANTIC_MODELS and action in PYDANTIC_MODELS[entity_name]

# =============================================================================
# ALIASES PARA ACCESO RÁPIDO (OPCIONAL)
# =============================================================================

# Acceso directo a modelos específicos
UsuarioCreateModel = PYDANTIC_MODELS["Usuario"]["create"]
UsuarioUpdateModel = PYDANTIC_MODELS["Usuario"]["update"]
UsuarioResponseModel = PYDANTIC_MODELS["Usuario"]["response"]

TareaCreateModel = PYDANTIC_MODELS["Tarea"]["create"]
TareaUpdateModel = PYDANTIC_MODELS["Tarea"]["update"]
TareaResponseModel = PYDANTIC_MODELS["Tarea"]["response"]

CategoriaCreateModel = PYDANTIC_MODELS["Categoria"]["create"]
CategoriaUpdateModel = PYDANTIC_MODELS["Categoria"]["update"]
CategoriaResponseModel = PYDANTIC_MODELS["Categoria"]["response"]

ArticuloCreateModel = PYDANTIC_MODELS["Articulo"]["create"]
ArticuloUpdateModel = PYDANTIC_MODELS["Articulo"]["update"]
ArticuloResponseModel = PYDANTIC_MODELS["Articulo"]["response"]
