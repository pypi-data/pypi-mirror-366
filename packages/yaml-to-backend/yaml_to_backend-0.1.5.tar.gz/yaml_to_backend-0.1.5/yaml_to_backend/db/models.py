"""Modelos SQLModel base generados automáticamente desde entidades YAML"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from .connection import Base


class Usuario(SQLModel, table=True):
    """Modelo generado para la entidad Usuario"""
    __tablename__ = 'usuarios'

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50)
    password: str = Field(max_length=200)
    rol: str = Field(max_length=50)
    deleted_at: datetime
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

class Tarea(SQLModel, table=True):
    """Modelo generado para la entidad Tarea"""
    __tablename__ = 'tareas'

    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(max_length=100)
    descripcion: str
    usuario_id: Optional[int] = Field(default=None, foreign_key='usuarios.id')
    completada: bool
    fecha_creacion: datetime
    deleted_at: datetime
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

class Categoria(SQLModel, table=True):
    """Modelo generado para la entidad Categoria"""
    __tablename__ = 'categorias'

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, unique=True)
    descripcion: str = Field(max_length=500)
    color: str = Field(max_length=7)
    activa: bool
    orden: int
    deleted_at: datetime
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

class Articulo(SQLModel, table=True):
    """Modelo generado para la entidad Articulo"""
    __tablename__ = 'articulos'

    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(max_length=200, unique=True)
    contenido: str = Field(max_length=5000)
    autor_id: Optional[int] = Field(default=None, foreign_key='usuarios.id')
    publicado: bool
    fecha_publicacion: datetime
    tags: str = Field(max_length=500)
    deleted_at: datetime
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)
