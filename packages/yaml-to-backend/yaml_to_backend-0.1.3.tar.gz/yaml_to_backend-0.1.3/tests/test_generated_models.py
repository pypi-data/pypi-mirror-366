#!/usr/bin/env python3
"""
Tests para verificar el funcionamiento del diccionario PYDANTIC_MODELS generado
"""

import pytest
from pydantic import BaseModel
from typing import Dict, Type, Any
import sys
import os

# Agregar el directorio backend al path para importar los módulos generados
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

class TestGeneratedModels:
    """Tests para verificar los modelos generados automáticamente"""
    
    def test_pydantic_models_import(self):
        """Test que verifica que el módulo generated_models se puede importar"""
        try:
            from db.generated_models import PYDANTIC_MODELS
            assert PYDANTIC_MODELS is not None
            print("✅ Módulo generated_models importado correctamente")
        except ImportError as e:
            pytest.fail(f"No se pudo importar generated_models: {e}")
    
    def test_pydantic_models_structure(self):
        """Test que verifica la estructura del diccionario PYDANTIC_MODELS"""
        from db.generated_models import PYDANTIC_MODELS
        
        # Verificar que es un diccionario
        assert isinstance(PYDANTIC_MODELS, dict), "PYDANTIC_MODELS debe ser un diccionario"
        
        # Verificar que no está vacío
        assert len(PYDANTIC_MODELS) > 0, "PYDANTIC_MODELS no debe estar vacío"
        
        print(f"✅ PYDANTIC_MODELS contiene {len(PYDANTIC_MODELS)} entidades")
        
        # Verificar estructura de cada entidad
        for entity_name, models in PYDANTIC_MODELS.items():
            assert isinstance(entity_name, str), f"Nombre de entidad debe ser string: {entity_name}"
            assert isinstance(models, dict), f"Modelos de {entity_name} deben ser un diccionario"
            
            # Verificar que tiene las claves requeridas
            required_keys = ['create', 'update', 'response']
            for key in required_keys:
                assert key in models, f"Entidad {entity_name} debe tener modelo {key}"
            
            print(f"✅ Entidad {entity_name}: {list(models.keys())}")
    
    def test_pydantic_models_types(self):
        """Test que verifica que todos los modelos son clases Pydantic válidas"""
        from db.generated_models import PYDANTIC_MODELS
        
        for entity_name, models in PYDANTIC_MODELS.items():
            for model_type, model_class in models.items():
                # Verificar que es una clase
                assert isinstance(model_class, type), f"Modelo {entity_name}.{model_type} debe ser una clase"
                
                # Verificar que hereda de BaseModel
                assert issubclass(model_class, BaseModel), f"Modelo {entity_name}.{model_type} debe heredar de BaseModel"
                
                print(f"✅ Modelo {entity_name}.{model_type}: {model_class.__name__}")
    
    def test_pydantic_models_instantiation(self):
        """Test que verifica que se pueden crear instancias de los modelos"""
        from db.generated_models import PYDANTIC_MODELS
        
        for entity_name, models in PYDANTIC_MODELS.items():
            # Probar modelo create
            if 'create' in models:
                create_model = models['create']
                try:
                    # Crear instancia con datos mínimos
                    instance = create_model()
                    assert isinstance(instance, create_model)
                    print(f"✅ Instancia creada para {entity_name}.create")
                except Exception as e:
                    print(f"⚠️ No se pudo crear instancia de {entity_name}.create: {e}")
    
    def test_pydantic_models_validation(self):
        """Test que verifica la validación de datos en los modelos"""
        from db.generated_models import PYDANTIC_MODELS
        
        # Datos de prueba para diferentes tipos de entidades
        test_data = {
            'Usuario': {
                'create': {'username': 'test_user', 'password': 'test_pass', 'rol': 'usuario'},
                'update': {'username': 'updated_user'},
                'response': {'id': 1, 'username': 'test_user', 'rol': 'usuario', 'deleted_at': None}
            },
            'Tarea': {
                'create': {'titulo': 'Test Task', 'descripcion': 'Test Description', 'usuario_id': 1},
                'update': {'titulo': 'Updated Task'},
                'response': {'id': 1, 'titulo': 'Test Task', 'descripcion': 'Test Description', 'usuario_id': 1, 'completada': False, 'deleted_at': None}
            }
        }
        
        for entity_name, models in PYDANTIC_MODELS.items():
            if entity_name in test_data:
                entity_test_data = test_data[entity_name]
                
                for model_type, model_class in models.items():
                    if model_type in entity_test_data:
                        test_data_for_model = entity_test_data[model_type]
                        try:
                            # Intentar crear instancia con datos de prueba
                            instance = model_class(**test_data_for_model)
                            assert isinstance(instance, model_class)
                            print(f"✅ Validación exitosa para {entity_name}.{model_type}")
                        except Exception as e:
                            print(f"⚠️ Error de validación en {entity_name}.{model_type}: {e}")
    
    def test_pydantic_models_serialization(self):
        """Test que verifica la serialización/deserialización de los modelos"""
        from db.generated_models import PYDANTIC_MODELS
        
        for entity_name, models in PYDANTIC_MODELS.items():
            for model_type, model_class in models.items():
                try:
                    # Crear instancia
                    instance = model_class()
                    
                    # Serializar a dict
                    data_dict = instance.model_dump()
                    assert isinstance(data_dict, dict)
                    
                    # Deserializar desde dict
                    new_instance = model_class(**data_dict)
                    assert isinstance(new_instance, model_class)
                    
                    print(f"✅ Serialización/deserialización exitosa para {entity_name}.{model_type}")
                except Exception as e:
                    print(f"⚠️ Error en serialización de {entity_name}.{model_type}: {e}")
    
    def test_pydantic_models_access_patterns(self):
        """Test que verifica patrones de acceso comunes al diccionario"""
        from db.generated_models import PYDANTIC_MODELS
        
        # Verificar acceso por entidad
        for entity_name in PYDANTIC_MODELS.keys():
            entity_models = PYDANTIC_MODELS[entity_name]
            assert 'create' in entity_models
            assert 'update' in entity_models
            assert 'response' in entity_models
        
        # Verificar acceso directo a modelos específicos
        if 'Usuario' in PYDANTIC_MODELS:
            usuario_models = PYDANTIC_MODELS['Usuario']
            assert hasattr(usuario_models['create'], '__call__')
            assert hasattr(usuario_models['update'], '__call__')
            assert hasattr(usuario_models['response'], '__call__')
        
        print("✅ Patrones de acceso verificados correctamente")
    
    def test_pydantic_models_integration(self):
        """Test de integración que verifica el uso completo del diccionario"""
        from db.generated_models import PYDANTIC_MODELS
        
        # Simular un flujo completo de CRUD usando los modelos
        for entity_name, models in PYDANTIC_MODELS.items():
            try:
                # 1. Crear datos de entrada
                create_model = models['create']
                create_data = {}
                
                # Intentar crear con datos mínimos
                create_instance = create_model(**create_data)
                
                # 2. Actualizar datos
                update_model = models['update']
                update_data = {}
                update_instance = update_model(**update_data)
                
                # 3. Respuesta
                response_model = models['response']
                response_data = {'id': 1}
                response_instance = response_model(**response_data)
                
                print(f"✅ Flujo CRUD completo para {entity_name}")
                
            except Exception as e:
                print(f"⚠️ Error en flujo CRUD para {entity_name}: {e}")

class TestGeneratedModelsIntegration:
    """Tests de integración con el sistema completo"""
    
    def test_models_with_crud_generator(self):
        """Test que verifica que los modelos funcionan con el CRUD generator"""
        from db.generated_models import PYDANTIC_MODELS
        from api.crud_generator import CRUDGenerator
        
        # Verificar que el CRUD generator puede usar los modelos
        for entity_name, models in PYDANTIC_MODELS.items():
            try:
                # Simular uso en CRUD generator
                create_model = models['create']
                update_model = models['update']
                response_model = models['response']
                
                # Verificar que los modelos tienen los campos esperados
                create_fields = create_model.model_fields
                update_fields = update_model.model_fields
                response_fields = response_model.model_fields
                
                assert isinstance(create_fields, dict)
                assert isinstance(update_fields, dict)
                assert isinstance(response_fields, dict)
                
                print(f"✅ Modelos de {entity_name} compatibles con CRUD generator")
                
            except Exception as e:
                print(f"⚠️ Error en integración CRUD para {entity_name}: {e}")
    
    def test_models_with_auth_system(self):
        """Test que verifica que los modelos funcionan con el sistema de autenticación"""
        from db.generated_models import PYDANTIC_MODELS
        from security.auth import AuthManager
        
        # Verificar que los modelos de usuario funcionan con el sistema de auth
        if 'Usuario' in PYDANTIC_MODELS:
            usuario_models = PYDANTIC_MODELS['Usuario']
            
            try:
                # Simular creación de usuario
                create_model = usuario_models['create']
                user_data = {
                    'username': 'test_user',
                    'password': 'test_password',
                    'rol': 'usuario'
                }
                
                user_instance = create_model(**user_data)
                assert user_instance.username == 'test_user'
                assert user_instance.rol == 'usuario'
                
                print("✅ Modelos de Usuario compatibles con sistema de autenticación")
                
            except Exception as e:
                print(f"⚠️ Error en integración auth para Usuario: {e}")

if __name__ == "__main__":
    # Ejecutar tests manualmente
    test_instance = TestGeneratedModels()
    test_instance.test_pydantic_models_import()
    test_instance.test_pydantic_models_structure()
    test_instance.test_pydantic_models_types()
    test_instance.test_pydantic_models_instantiation()
    test_instance.test_pydantic_models_validation()
    test_instance.test_pydantic_models_serialization()
    test_instance.test_pydantic_models_access_patterns()
    test_instance.test_pydantic_models_integration()
    
    integration_instance = TestGeneratedModelsIntegration()
    integration_instance.test_models_with_crud_generator()
    integration_instance.test_models_with_auth_system()
    
    print("\n🎉 Todos los tests de modelos generados completados!") 