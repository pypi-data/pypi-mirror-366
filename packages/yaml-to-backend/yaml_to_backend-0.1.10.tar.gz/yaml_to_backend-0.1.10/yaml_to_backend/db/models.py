"""Modelos SQLModel base generados automáticamente desde entidades YAML"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from yaml_to_backend.db.connection import Base


class AplicacionImagen(SQLModel, table=True):
    """Modelo generado para la entidad AplicacionImagen"""
    __tablename__ = 'aplicacion_imagen'

    id: Optional[int] = Field(default=None, primary_key=True)
    aplicacion: Optional[int] = Field(default=None, foreign_key='aplicaciones.id')
    imagen: Optional[int] = Field(default=None, foreign_key='imagenes.id')
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    habilitado: bool = Field(default=True)

class Perfiles(SQLModel, table=True):
    """Modelo generado para la entidad Perfiles"""
    __tablename__ = 'perfiles'

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    email: str = Field(max_length=255)
    imagen: Optional[str] = Field(max_length=255, default=None)
    usuario: Optional[int] = Field(default=None, foreign_key='usuarios.id')
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    habilitado: bool = Field(default=True)

class Contenedores(SQLModel, table=True):
    """Modelo generado para la entidad Contenedores"""
    __tablename__ = 'contenedores'

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    http: Optional[int] = Field(default=None)
    https: Optional[int] = Field(default=None)
    puertos: Optional[str] = Field(default=None)
    redes: Optional[str] = Field(default=None)
    variables: Optional[str] = Field(default=None)
    volumenes: Optional[str] = Field(default=None)
    imagen: Optional[int] = Field(default=None, foreign_key='imagenes.id')
    usuario: Optional[int] = Field(default=None, foreign_key='usuarios.id')
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    habilitado: bool = Field(default=True)

class Imagenes(SQLModel, table=True):
    """Modelo generado para la entidad Imagenes"""
    __tablename__ = 'imagenes'

    id: Optional[int] = Field(default=None, primary_key=True)
    ubicacion: str = Field(max_length=255)
    nombre: str = Field(max_length=100)
    comandos: Optional[str] = Field(default=None)
    logo: Optional[str] = Field(max_length=255, default=None)
    sistemaOperativo: Optional[int] = Field(default=None, foreign_key='sistemas_operativos.id')
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    habilitado: bool = Field(default=True)

class Aplicaciones(SQLModel, table=True):
    """Modelo generado para la entidad Aplicaciones"""
    __tablename__ = 'aplicaciones'

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    comando: str = Field(max_length=255)
    sistemaOperativo: Optional[int] = Field(default=None, foreign_key='sistemas_operativos.id')
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    habilitado: bool = Field(default=True)

class SistemasOperativos(SQLModel, table=True):
    """Modelo generado para la entidad SistemasOperativos"""
    __tablename__ = 'sistemas_operativos'

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    logo: Optional[str] = Field(max_length=255, default=None)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    habilitado: bool = Field(default=True)

class Roles(SQLModel, table=True):
    """Modelo generado para la entidad Roles"""
    __tablename__ = 'roles'

    id: Optional[int] = Field(default=None, primary_key=True)
    rol: str = Field(max_length=100)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    habilitado: bool = Field(default=True)

class Usuario(SQLModel, table=True):
    """Modelo generado para la entidad Usuario"""
    __tablename__ = 'usuarios'

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(max_length=255)
    rol: str = Field(max_length=50)
    habilitado: bool
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default=None)

class Tarea(SQLModel, table=True):
    """Modelo generado para la entidad Tarea"""
    __tablename__ = 'tareas'

    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(max_length=200)
    descripcion: Optional[str] = Field(default=None)
    completada: bool
    usuario_id: Optional[int] = Field(default=None, foreign_key='usuarios.id')
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = Field(default=None)
    habilitado: bool = Field(default=True)
