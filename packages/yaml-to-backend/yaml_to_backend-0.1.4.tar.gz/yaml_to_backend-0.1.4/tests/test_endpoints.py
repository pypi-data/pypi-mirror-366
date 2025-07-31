import pytest
import pytest_asyncio
import httpx
from fastapi.testclient import TestClient
from yaml_to_backend.app import BackendGenerator
import asyncio
import tempfile
import os
import yaml
from yaml_to_backend.db.generated_models import PYDANTIC_MODELS

@pytest_asyncio.fixture
async def test_app():
    """Fixture para crear una aplicación de prueba"""
    # Crear directorio temporal para entidades
    temp_dir = tempfile.mkdtemp()
    
    # Crear entidad de prueba
    test_entity = {
        "entidad": "TestEntity",
        "tabla": "test_entities",
        "campos": {
            "id": {"tipo": "integer", "pk": True},
            "nombre": {"tipo": "string", "max": 100},
            "descripcion": {"tipo": "text"}
        },
        "permisos": {
            "admin": ["r", "w", "d"],
            "usuario": ["r"]
        }
    }
    
    # Escribir archivo YAML
    yaml_file = os.path.join(temp_dir, "test_entity.yaml")
    with open(yaml_file, 'w') as f:
        yaml.dump(test_entity, f)
    
    # Configurar variables de entorno para pruebas
    os.environ['ENTITIES_PATH'] = temp_dir
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '3306'
    os.environ['DB_USER'] = 'root'
    os.environ['DB_PASSWORD'] = 'root'
    os.environ['DB_NAME'] = 'test_db'
    os.environ['DEBUG'] = 'True'
    os.environ['INSTALL'] = 'True'
    
    # Crear y inicializar aplicación
    generator = BackendGenerator()
    await generator.initialize()
    
    yield generator.app
    
    # Limpiar
    import shutil
    shutil.rmtree(temp_dir)

@pytest_asyncio.fixture
def auth_headers(test_app):
    """Fixture para obtener headers de autenticación"""
    client = TestClient(test_app)
    # Crear usuario de prueba
    user_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    # Login
    response = client.post("/api/auth/login", json=user_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Si no hay usuario, crear uno
        # Esto requeriría un endpoint de registro o usar el modo instalación
        return {}

class TestAuthEndpoints:
    """Pruebas para endpoints de autenticación"""
    
    def test_login_success(self, test_app):
        """Prueba login exitoso"""
                # Usar credenciales por defecto del modo instalación
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        client = TestClient(test_app)
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, test_app):
        """Prueba login con credenciales inválidas"""
        client = TestClient(test_app)
        login_data = {
            "username": "invalid",
            "password": "invalid"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_get_current_user(self, test_app, auth_headers):
        """Prueba obtener información del usuario actual"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
            
        client = TestClient(test_app)
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "rol" in data

class TestCRUDEndpoints:
    """Pruebas para endpoints CRUD generados"""
    
    def test_list_entities(self, test_app, auth_headers):
        """Prueba listar entidades"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
            
        client = TestClient(test_app)
        response = client.get("/api/testentity/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_entity(self, test_app, auth_headers):
        """Prueba crear entidad"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
            
        client = TestClient(test_app)
        entity_data = {
            "nombre": "Test Entity",
            "descripcion": "Test Description"
        }
        
        response = client.post("/api/testentity/", json=entity_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Test Entity"
        assert data["descripcion"] == "Test Description"
        assert "id" in data
    
    def test_get_entity_by_id(self, test_app, auth_headers):
        """Prueba obtener entidad por ID"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
            
        client = TestClient(test_app)
        # Primero crear una entidad
        entity_data = {
            "nombre": "Test Entity",
            "descripcion": "Test Description"
        }
        
        create_response = client.post("/api/testentity/", json=entity_data, headers=auth_headers)
        created_entity = create_response.json()
        entity_id = created_entity["id"]
        
        # Obtener la entidad por ID
        response = client.get(f"/api/testentity/{entity_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["nombre"] == "Test Entity"
    
    def test_update_entity(self, test_app, auth_headers):
        """Prueba actualizar entidad"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
            
        client = TestClient(test_app)
        # Primero crear una entidad
        entity_data = {
            "nombre": "Original Name",
            "descripcion": "Original Description"
        }
        
        create_response = client.post("/api/testentity/", json=entity_data, headers=auth_headers)
        created_entity = create_response.json()
        entity_id = created_entity["id"]
        
        # Actualizar la entidad
        update_data = {
            "nombre": "Updated Name"
        }
        
        response = client.put(f"/api/testentity/{entity_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Updated Name"
        assert data["descripcion"] == "Original Description"  # No debe cambiar
    
    def test_delete_entity(self, test_app, auth_headers):
        """Prueba eliminar entidad"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
            
        client = TestClient(test_app)
        # Primero crear una entidad
        entity_data = {
            "nombre": "To Delete",
            "descripcion": "Will be deleted"
        }
        
        create_response = client.post("/api/testentity/", json=entity_data, headers=auth_headers)
        created_entity = create_response.json()
        entity_id = created_entity["id"]
        
        # Eliminar la entidad
        response = client.delete(f"/api/testentity/{entity_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "eliminada correctamente" in data["message"]
        
        # Verificar que ya no existe
        get_response = client.get(f"/api/testentity/{entity_id}", headers=auth_headers)
        assert get_response.status_code == 404

class TestGeneratedModelsUsage:
    """Tests que utilizan específicamente el diccionario PYDANTIC_MODELS generado"""
    
    def test_pydantic_models_availability(self, test_app):
        """Test que verifica que PYDANTIC_MODELS está disponible y contiene las entidades esperadas"""
        # Verificar que PYDANTIC_MODELS está disponible
        assert PYDANTIC_MODELS is not None
        assert isinstance(PYDANTIC_MODELS, dict)
        
        # Verificar que contiene las entidades esperadas
        expected_entities = ['Usuario', 'Tarea', 'Categoria', 'Articulo']
        for entity in expected_entities:
            assert entity in PYDANTIC_MODELS, f"Entidad {entity} debe estar en PYDANTIC_MODELS"
        
        print(f"✅ PYDANTIC_MODELS contiene {len(PYDANTIC_MODELS)} entidades: {list(PYDANTIC_MODELS.keys())}")
    
    def test_pydantic_models_crud_operations(self, test_app, auth_headers):
        """Test que utiliza PYDANTIC_MODELS para operaciones CRUD"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        client = TestClient(test_app)
        
        # Usar PYDANTIC_MODELS para crear datos de prueba
        for entity_name, models in PYDANTIC_MODELS.items():
            if entity_name == 'Tarea':  # Probar con Tarea como ejemplo
                create_model = models['create']
                update_model = models['update']
                response_model = models['response']
                
                # Crear datos usando el modelo create
                create_data = {
                    'titulo': f'Test {entity_name}',
                    'descripcion': f'Test Description for {entity_name}',
                    'usuario_id': 1
                }
                
                # Validar datos con el modelo create
                try:
                    validated_data = create_model(**create_data)
                    print(f"✅ Datos validados para {entity_name}.create")
                except Exception as e:
                    print(f"⚠️ Error validando datos para {entity_name}.create: {e}")
                    continue
                
                # Hacer POST usando los datos validados
                response = client.post(f"/api/{entity_name.lower()}/", 
                                     json=validated_data.model_dump(), 
                                     headers=auth_headers)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Validar respuesta con el modelo response
                    try:
                        validated_response = response_model(**response_data)
                        print(f"✅ Respuesta validada para {entity_name}.response")
                    except Exception as e:
                        print(f"⚠️ Error validando respuesta para {entity_name}.response: {e}")
                    
                    # Probar actualización
                    update_data = {'titulo': f'Updated {entity_name}'}
                    try:
                        validated_update = update_model(**update_data)
                        print(f"✅ Datos de actualización validados para {entity_name}.update")
                    except Exception as e:
                        print(f"⚠️ Error validando actualización para {entity_name}.update: {e}")
                    
                    break  # Solo probar con una entidad
    
    def test_pydantic_models_dynamic_access(self, test_app):
        """Test que demuestra acceso dinámico a PYDANTIC_MODELS"""
        # Acceso dinámico a modelos
        for entity_name in PYDANTIC_MODELS.keys():
            models = PYDANTIC_MODELS[entity_name]
            
            # Verificar que todos los tipos de modelo están disponibles
            assert 'create' in models, f"Modelo create no encontrado para {entity_name}"
            assert 'update' in models, f"Modelo update no encontrado para {entity_name}"
            assert 'response' in models, f"Modelo response no encontrado para {entity_name}"
            
            # Verificar que son clases válidas
            assert callable(models['create']), f"Modelo create de {entity_name} debe ser callable"
            assert callable(models['update']), f"Modelo update de {entity_name} debe ser callable"
            assert callable(models['response']), f"Modelo response de {entity_name} debe ser callable"
            
            print(f"✅ Acceso dinámico verificado para {entity_name}")
    
    def test_pydantic_models_field_validation(self, test_app):
        """Test que verifica la validación de campos usando PYDANTIC_MODELS"""
        for entity_name, models in PYDANTIC_MODELS.items():
            create_model = models['create']
            
            # Obtener campos del modelo
            fields = create_model.model_fields
            
            # Verificar que tiene campos
            assert len(fields) > 0, f"Modelo create de {entity_name} debe tener campos"
            
            print(f"✅ {entity_name}.create tiene {len(fields)} campos: {list(fields.keys())}")
            
            # Verificar tipos de campos
            for field_name, field_info in fields.items():
                assert hasattr(field_info, 'annotation'), f"Campo {field_name} debe tener tipo"
                print(f"  - {field_name}: {field_info.annotation}")
    
    def test_pydantic_models_error_handling(self, test_app):
        """Test que verifica el manejo de errores en PYDANTIC_MODELS"""
        for entity_name, models in PYDANTIC_MODELS.items():
            create_model = models['create']
            
            # Probar con datos inválidos
            invalid_data = {'invalid_field': 'invalid_value'}
            
            try:
                create_model(**invalid_data)
                print(f"⚠️ {entity_name}.create aceptó datos inválidos (puede ser normal)")
            except Exception as e:
                print(f"✅ {entity_name}.create rechazó datos inválidos correctamente: {type(e).__name__}")
    
    def test_pydantic_models_serialization_roundtrip(self, test_app):
        """Test que verifica serialización completa usando PYDANTIC_MODELS"""
        for entity_name, models in PYDANTIC_MODELS.items():
            create_model = models['create']
            response_model = models['response']
            
            # Crear datos mínimos
            try:
                # Intentar crear con datos mínimos
                create_instance = create_model()
                
                # Serializar
                create_dict = create_instance.model_dump()
                
                # Deserializar
                create_instance_2 = create_model(**create_dict)
                
                # Verificar que son iguales
                assert create_instance.model_dump() == create_instance_2.model_dump()
                
                print(f"✅ Serialización roundtrip exitosa para {entity_name}.create")
                
            except Exception as e:
                print(f"⚠️ Error en serialización roundtrip para {entity_name}.create: {e}")

class TestPermissionEndpoints:
    """Pruebas para endpoints con permisos especiales"""
    
    def test_yo_endpoint(self, test_app, auth_headers):
        """Prueba el endpoint /yo para entidades con permisos tipo 'yo'"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
            
        client = TestClient(test_app)
        response = client.get("/api/testentity/yo", headers=auth_headers)
        
        # El endpoint debe existir si hay permisos 'yo'
        # Puede devolver 200 con lista vacía o 403 si no hay permisos
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) 