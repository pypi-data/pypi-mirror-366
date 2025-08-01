"""
Integration tests for Django Revolution.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from django_revolution.config import DjangoRevolutionSettings
from django_revolution.zones import ZoneManager, ZoneDetector
from django_revolution.openapi.generator import OpenAPIGenerator


class TestFullWorkflow:
    """Test full workflow integration."""

    def setup_method(self):
        """Set up test configuration."""
        self.config = DjangoRevolutionSettings(
            zones={
                "public": {
                    "apps": ["django.contrib.auth"],
                    "title": "Public API",
                    "version": "v1"
                },
                "admin": {
                    "apps": ["django.contrib.admin"],
                    "title": "Admin API",
                    "version": "v1"
                }
            }
        )

    def test_zone_manager_creation(self):
        """Test ZoneManager creation and zone detection."""
        zone_manager = ZoneManager(self.config)
        
        assert len(zone_manager.zones) == 2
        assert "public" in zone_manager.zones
        assert "admin" in zone_manager.zones
        
        public_zone = zone_manager.zones["public"]
        assert public_zone.name == "public"
        assert public_zone.apps == ["django.contrib.auth", "django.contrib.contenttypes"]
        assert public_zone.public is True

    def test_zone_detector_creation(self):
        """Test ZoneDetector creation."""
        zone_detector = ZoneDetector(self.config)
        
        assert zone_detector.config == self.config
        assert len(zone_detector.zones) == 2

    def test_openapi_generator_creation(self):
        """Test OpenAPIGenerator creation."""
        generator = OpenAPIGenerator(self.config)
        
        assert generator.config == self.config
        assert generator.zone_manager is not None
        assert len(generator.zone_manager.zones) == 2

    def test_schema_generation_workflow(self, tmp_path):
        """Test complete schema generation workflow."""
        # Mock manage.py
        manage_py = tmp_path / "manage.py"
        manage_py.write_text("# Mock manage.py")
        
        with patch('django_revolution.openapi.generator.get_django_manage_py') as mock_manage_py:
            mock_manage_py.return_value = manage_py
            
            generator = OpenAPIGenerator(self.config)
            
            # Mock run_command to simulate successful schema generation
            with patch('django_revolution.openapi.generator.run_command') as mock_run_command:
                mock_run_command.return_value = (True, "Success")
                
                # Mock zone manager
                with patch.object(generator.zone_manager, 'create_dynamic_urlconf_module') as mock_create_module:
                    mock_create_module.return_value = Mock(__name__="mock_urls")
                    
                    # Generate schemas
                    schemas = generator.generate_schemas()
                    
                    # Should generate schemas for both zones
                    assert len(schemas) == 2
                    assert "public" in schemas
                    assert "admin" in schemas

    def test_client_generation_workflow(self, tmp_path):
        """Test complete client generation workflow."""
        # Mock manage.py
        manage_py = tmp_path / "manage.py"
        manage_py.write_text("# Mock manage.py")
        
        with patch('django_revolution.openapi.generator.get_django_manage_py') as mock_manage_py:
            mock_manage_py.return_value = manage_py
            
            generator = OpenAPIGenerator(self.config)
            
            # Mock schemas
            schemas = {
                "public": tmp_path / "public.yaml",
                "admin": tmp_path / "admin.yaml"
            }
            
            # Create mock schema files
            for schema_path in schemas.values():
                schema_path.write_text("# Mock schema")
            
            # Mock TypeScript generator
            generator.ts_generator = Mock()
            generator.ts_generator.generate_client.return_value = Mock(
                success=True,
                zone_name="test",
                output_path=tmp_path,
                files_generated=5,
                error_message=""
            )
            
            # Mock Python generator
            generator.python_generator = Mock()
            generator.python_generator.generate_client.return_value = Mock(
                success=True,
                zone_name="test",
                output_path=tmp_path,
                files_generated=3,
                error_message=""
            )
            
            # Generate TypeScript clients
            ts_results = generator.generate_typescript_clients(schemas)
            assert len(ts_results) == 2
            
            # Generate Python clients
            py_results = generator.generate_python_clients(schemas)
            assert len(py_results) == 2

    def test_full_generation_pipeline(self, tmp_path):
        """Test the complete generation pipeline."""
        # Mock manage.py
        manage_py = tmp_path / "manage.py"
        manage_py.write_text("# Mock manage.py")
        
        with patch('django_revolution.openapi.generator.get_django_manage_py') as mock_manage_py:
            mock_manage_py.return_value = manage_py
            
            generator = OpenAPIGenerator(self.config)
            
            # Mock all external dependencies
            with patch('django_revolution.openapi.generator.run_command') as mock_run_command:
                mock_run_command.return_value = (True, "Success")
                
                with patch.object(generator.zone_manager, 'create_dynamic_urlconf_module') as mock_create_module:
                    mock_create_module.return_value = Mock(__name__="mock_urls")
                    
                    # Mock generators
                    generator.ts_generator = Mock()
                    generator.ts_generator.generate_client.return_value = Mock(
                        success=True,
                        zone_name="test",
                        output_path=tmp_path,
                        files_generated=5,
                        error_message=""
                    )
                    
                    generator.python_generator = Mock()
                    generator.python_generator.generate_client.return_value = Mock(
                        success=True,
                        zone_name="test",
                        output_path=tmp_path,
                        files_generated=3,
                        error_message=""
                    )
                    
                    # Run full generation
                    summary = generator.generate_all()
                    
                    # Verify results
                    assert summary.total_zones == 2
                    assert summary.successful_typescript == 2
                    assert summary.successful_python == 2
                    assert summary.failed_typescript == 0
                    assert summary.failed_python == 0
                    assert summary.total_files_generated > 0
                    assert summary.duration_seconds > 0


class TestMultithreadingIntegration:
    """Integration tests for multithreading functionality."""

    def test_multithreading_configuration_integration(self):
        """Test that multithreading configuration is properly integrated."""
        config = DjangoRevolutionSettings(
            enable_multithreading=True,
            max_workers=4,
            zones={
                "zone1": {
                    "apps": ["django.contrib.auth"],
                    "title": "Zone 1",
                    "version": "v1"
                },
                "zone2": {
                    "apps": ["django.contrib.contenttypes"],
                    "title": "Zone 2",
                    "version": "v1"
                }
            }
        )
        
        assert config.enable_multithreading is True
        assert config.max_workers == 4
        
        # Test that configuration is passed to components
        zone_manager = ZoneManager(config)
        assert zone_manager.config.enable_multithreading is True
        assert zone_manager.config.max_workers == 4
        
        zone_detector = ZoneDetector(config)
        assert zone_detector.config.enable_multithreading is True
        assert zone_detector.config.max_workers == 4

    def test_zone_manager_multithreading_integration(self):
        """Test ZoneManager integration with multithreading."""
        config = DjangoRevolutionSettings(
            enable_multithreading=True,
            max_workers=2,
            zones={
                "public": {
                    "apps": ["django.contrib.auth"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        zone_manager = ZoneManager(config)
        
        # Verify that multithreading settings are accessible
        assert zone_manager.config.enable_multithreading is True
        assert zone_manager.config.max_workers == 2

    def test_openapi_generator_multithreading_integration(self):
        """Test OpenAPIGenerator integration with multithreading."""
        config = DjangoRevolutionSettings(
            enable_multithreading=True,
            max_workers=3,
            zones={
                "public": {
                    "apps": ["django.contrib.auth"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        generator = OpenAPIGenerator(config)
        
        # Verify that multithreading settings are accessible
        assert generator.config.enable_multithreading is True
        assert generator.config.max_workers == 3
        
        # Test status includes multithreading info
        status = generator.get_status()
        assert "multithreading" in status
        assert status["multithreading"]["enabled"] is True
        assert status["multithreading"]["max_workers"] == 3

    def test_sequential_fallback_integration(self):
        """Test sequential fallback integration."""
        config = DjangoRevolutionSettings(
            enable_multithreading=False,  # Disable multithreading
            max_workers=4,
            zones={
                "single": {
                    "apps": ["django.contrib.auth"],
                    "title": "Single Zone",
                    "version": "v1"
                }
            }
        )
        
        generator = OpenAPIGenerator(config)
        
        # Verify that multithreading is disabled
        assert generator.config.enable_multithreading is False
        
        # Test status reflects disabled multithreading
        status = generator.get_status()
        assert status["multithreading"]["enabled"] is False

    def test_single_zone_fallback_integration(self):
        """Test single zone fallback integration."""
        config = DjangoRevolutionSettings(
            enable_multithreading=True,
            max_workers=4,
            zones={
                "single": {
                    "apps": ["django.contrib.auth"],
                    "title": "Single Zone",
                    "version": "v1"
                }
            }
        )
        
        generator = OpenAPIGenerator(config)
        
        # Verify that multithreading is enabled but will fall back for single zone
        assert generator.config.enable_multithreading is True
        assert len(generator.zone_manager.zones) == 1 