import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
import tempfile
import os
import yaml
from yaml_to_backend.core.entity_parser import EntityParser
from yaml_to_backend.core.model_generator import ModelGenerator
from yaml_to_backend.security.auth import AuthManager
from yaml_to_backend.api.crud_generator import CRUDGenerator
from yaml_to_backend.api.auth_routes import router as auth_router

@pytest_asyncio.fixture
async def test_app():
    """Fixture para crear una aplicación de prueba simplificada"""
    app = FastAPI(title="Test Backend")
    
    # Incluir rutas de autenticación
    app.include_router(auth_router)
    
    return app

@pytest_asyncio.fixture
async def auth_headers(test_app):
    """Fixture para obtener headers de autenticación"""
    async with AsyncClient(app=test_app, base_url="http://testserver") as ac:
        # Usar credenciales por defecto
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = await ac.post("/api/auth/login", json=login_data)
            if response.status_code == 200:
                token = response.json()["access_token"]
                return {"Authorization": f"Bearer {token}"}
        except:
            pass
        
        return {}

class TestAuthEndpoints:
    """Pruebas para endpoints de autenticación"""
    
    def test_login_endpoint_exists(self, test_app):
        """Prueba que el endpoint de login existe"""
        from fastapi.testclient import TestClient
        
        client = TestClient(test_app)
        response = client.post("/api/auth/login", json={
            "username": "test",
            "password": "test"
        })
        
        # Debe responder (puede ser 401, 422 o 500, pero no 404)
        assert response.status_code in [401, 422, 500]
    
    def test_me_endpoint_exists(self, test_app):
        """Prueba que el endpoint /me existe"""
        from fastapi.testclient import TestClient
        
        client = TestClient(test_app)
        response = client.get("/api/auth/me")
        
        # Debe responder (puede ser 401, pero no 404)
        assert response.status_code in [401, 403]

class TestEntityParser:
    """Pruebas para el parser de entidades"""
    
    def test_entity_parser_creation(self):
        """Prueba la creación del parser de entidades"""
        parser = EntityParser("./entidades/")
        assert parser is not None
        assert str(parser.entities_path) == "entidades"
    
    def test_model_generator_creation(self):
        """Prueba la creación del generador de modelos"""
        generator = ModelGenerator()
        assert generator is not None
        assert generator.generated_models == {}
        assert generator.pydantic_models == {}
    
    def test_auth_manager_creation(self):
        """Prueba la creación del gestor de autenticación"""
        auth_manager = AuthManager(
            secret_key="test_key",
            algorithm="HS256",
            access_token_expire_minutes=30
        )
        assert auth_manager is not None
        assert auth_manager.secret_key == "test_key"
    
    def test_crud_generator_creation(self):
        """Prueba la creación del generador CRUD"""
        auth_manager = AuthManager("test_key")
        crud_generator = CRUDGenerator(auth_manager)
        assert crud_generator is not None
        assert crud_generator.auth_manager == auth_manager

class TestYAMLEntities:
    """Pruebas para los archivos YAML de entidades"""
    
    def test_usuario_yaml_exists(self):
        """Prueba que el archivo usuario.yaml existe y es válido"""
        yaml_path = "entidades/usuario.yaml"
        assert os.path.exists(yaml_path), f"El archivo {yaml_path} no existe"
        
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "entidad" in data
        assert "tabla" in data
        assert "campos" in data
        assert "permisos" in data
        assert data["entidad"] == "Usuario"
    
    def test_tarea_yaml_exists(self):
        """Prueba que el archivo tarea.yaml existe y es válido"""
        yaml_path = "entidades/tarea.yaml"
        assert os.path.exists(yaml_path), f"El archivo {yaml_path} no existe"
        
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "entidad" in data
        assert "tabla" in data
        assert "campos" in data
        assert "permisos" in data
        assert data["entidad"] == "Tarea"
    
    def test_yaml_structure(self):
        """Prueba la estructura de los archivos YAML"""
        yaml_files = ["entidades/usuario.yaml", "entidades/tarea.yaml"]
        
        for yaml_file in yaml_files:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Verificar campos requeridos
            required_fields = ["entidad", "tabla", "campos"]
            for field in required_fields:
                assert field in data, f"Campo '{field}' faltante en {yaml_file}"
            
            # Verificar que hay campos definidos
            assert len(data["campos"]) > 0, f"No hay campos definidos en {yaml_file}"
            
            # Verificar que hay al menos un campo con pk
            has_pk = any(field.get("pk") for field in data["campos"].values())
            assert has_pk, f"No hay campo con pk en {yaml_file}" 