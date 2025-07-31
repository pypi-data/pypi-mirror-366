import pytest
import tempfile
import os
import yaml
from yaml_to_backend.core.entity_parser import EntityParser

class TestEntityParser:
    """Pruebas para el parser de entidades"""
    
    def test_parser_initialization(self, temp_entities_dir):
        """Prueba la inicialización del parser"""
        parser = EntityParser(temp_entities_dir)
        assert str(parser.entities_path) == temp_entities_dir
        assert parser.entities == {}
    
    def test_load_entities_from_yaml(self, temp_entities_dir, sample_entity_data):
        """Prueba la carga de entidades desde archivos YAML"""
        # Crear archivo YAML de prueba
        yaml_file = os.path.join(temp_entities_dir, "test_entity.yaml")
        with open(yaml_file, 'w') as f:
            yaml.dump(sample_entity_data, f)
        
        # Cargar entidades
        parser = EntityParser(temp_entities_dir)
        entities = parser.load_entities()
        
        assert "TestEntity" in entities
        assert entities["TestEntity"]["entidad"] == "TestEntity"
        assert entities["TestEntity"]["tabla"] == "test_entities"
        assert "campos" in entities["TestEntity"]
        assert "permisos" in entities["TestEntity"]
    
    def test_load_multiple_entities(self, temp_entities_dir):
        """Prueba la carga de múltiples entidades"""
        # Crear primera entidad
        entity1 = {
            "entidad": "Entity1",
            "tabla": "entity1",
            "campos": {"id": {"tipo": "integer", "pk": True}}
        }
        
        # Crear segunda entidad
        entity2 = {
            "entidad": "Entity2",
            "tabla": "entity2",
            "campos": {"id": {"tipo": "integer", "pk": True}}
        }
        
        # Escribir archivos
        with open(os.path.join(temp_entities_dir, "entity1.yaml"), 'w') as f:
            yaml.dump(entity1, f)
        
        with open(os.path.join(temp_entities_dir, "entity2.yaml"), 'w') as f:
            yaml.dump(entity2, f)
        
        # Cargar entidades
        parser = EntityParser(temp_entities_dir)
        entities = parser.load_entities()
        
        assert "Entity1" in entities
        assert "Entity2" in entities
        assert len(entities) == 2
    
    def test_get_entity(self, temp_entities_dir, sample_entity_data):
        """Prueba la obtención de una entidad específica"""
        # Crear archivo YAML
        yaml_file = os.path.join(temp_entities_dir, "test_entity.yaml")
        with open(yaml_file, 'w') as f:
            yaml.dump(sample_entity_data, f)
        
        # Cargar y obtener entidad
        parser = EntityParser(temp_entities_dir)
        parser.load_entities()
        
        entity = parser.get_entity("TestEntity")
        assert entity is not None
        assert entity["entidad"] == "TestEntity"
        
        # Entidad inexistente
        non_existent = parser.get_entity("NonExistent")
        assert non_existent is None
    
    def test_validate_entity(self, temp_entities_dir):
        """Prueba la validación de entidades"""
        parser = EntityParser(temp_entities_dir)
        
        # Entidad válida
        valid_entity = {
            "entidad": "ValidEntity",
            "tabla": "valid_entities",
            "campos": {"id": {"tipo": "integer", "pk": True}}
        }
        assert parser.validate_entity(valid_entity) is True
        
        # Entidad sin campos requeridos
        invalid_entity1 = {
            "entidad": "InvalidEntity",
            "tabla": "invalid_entities"
            # Falta 'campos'
        }
        assert parser.validate_entity(invalid_entity1) is False
        
        # Entidad sin campos
        invalid_entity2 = {
            "entidad": "InvalidEntity",
            "tabla": "invalid_entities",
            "campos": {}
        }
        assert parser.validate_entity(invalid_entity2) is False
    
    def test_load_entities_empty_directory(self, temp_entities_dir):
        """Prueba la carga desde un directorio vacío"""
        parser = EntityParser(temp_entities_dir)
        entities = parser.load_entities()
        assert entities == {}
    
    def test_load_entities_invalid_yaml(self, temp_entities_dir):
        """Prueba la carga de archivos YAML inválidos"""
        # Crear archivo YAML inválido
        invalid_yaml_file = os.path.join(temp_entities_dir, "invalid.yaml")
        with open(invalid_yaml_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        # Crear archivo YAML válido
        valid_entity = {
            "entidad": "ValidEntity",
            "tabla": "valid_entities",
            "campos": {"id": {"tipo": "integer", "pk": True}}
        }
        valid_yaml_file = os.path.join(temp_entities_dir, "valid.yaml")
        with open(valid_yaml_file, 'w') as f:
            yaml.dump(valid_entity, f)
        
        # Cargar entidades (debe ignorar el archivo inválido)
        parser = EntityParser(temp_entities_dir)
        entities = parser.load_entities()
        
        assert "ValidEntity" in entities
        assert len(entities) == 1 