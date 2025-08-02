"""
Tests for Django Revolution multithreading functionality.
"""

import time
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from django_revolution.config import DjangoRevolutionSettings
from django_revolution.openapi.generator import OpenAPIGenerator
from django_revolution.zones import ZoneModel


class TestMultithreading:
    """Test multithreading functionality."""

    @pytest.fixture
    def sample_config(self):
        """Create sample configuration for testing."""
        return DjangoRevolutionSettings(
            enable_multithreading=True,
            max_workers=4,
            zones={
                "public": {
                    "apps": ["django.contrib.auth", "django.contrib.contenttypes"],
                    "title": "Public API",
                    "description": "Public API endpoints",
                    "public": True,
                    "version": "v1"
                },
                "admin": {
                    "apps": ["django.contrib.admin"],
                    "title": "Admin API", 
                    "description": "Admin API endpoints",
                    "public": False,
                    "version": "v1"
                },
                "api": {
                    "apps": ["rest_framework"],
                    "title": "API",
                    "description": "Main API endpoints",
                    "public": True,
                    "version": "v1"
                }
            }
        )

    @pytest.fixture
    def mock_generator(self, sample_config, tmp_path):
        """Create a mock generator for testing."""
        with patch('django_revolution.openapi.generator.get_django_manage_py') as mock_manage_py:
            mock_manage_py.return_value = tmp_path / "manage.py"
            
            # Create mock manage.py file
            (tmp_path / "manage.py").write_text("# Mock manage.py")
            
            generator = OpenAPIGenerator(sample_config)
            generator.output_dir = tmp_path / "openapi"
            generator.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Mock the zone manager
            generator.zone_manager = Mock()
            generator.zone_manager.zones = sample_config.get_zones()
            
            # Mock create_dynamic_urlconf_module
            def mock_create_module(zone_name, zone):
                mock_module = Mock()
                mock_module.__name__ = f"mock_{zone_name}_urls"
                return mock_module
            
            generator.zone_manager.create_dynamic_urlconf_module = mock_create_module
            
            return generator

    def test_multithreading_configuration(self, sample_config):
        """Test that multithreading configuration is properly set."""
        assert sample_config.enable_multithreading is True
        assert sample_config.max_workers == 4

    def test_single_zone_sequential_fallback(self, mock_generator):
        """Test that single zone falls back to sequential generation."""
        # Configure single zone
        mock_generator.config.enable_multithreading = True
        mock_generator.config.max_workers = 4
        mock_generator.zone_manager.zones = {
            "single": ZoneModel(
                name="single",
                apps=["django.contrib.auth"],
                title="Single Zone",
                version="v1"
            )
        }

        with patch('django_revolution.openapi.generator.run_command') as mock_run_command, \
             patch('django_revolution.openapi.generator.find_manage_py') as mock_find_manage_py:
            mock_run_command.return_value = (True, "Success")
            mock_find_manage_py.return_value = Path("/tmp/manage.py")
            
            schemas = mock_generator.generate_schemas()
            
            # Should use sequential generation for single zone
            assert len(schemas) == 1
            mock_run_command.assert_called_once()

    def test_multithreading_disabled_fallback(self, mock_generator):
        """Test that disabled multithreading uses sequential generation."""
        mock_generator.config.enable_multithreading = False
        mock_generator.config.max_workers = 4

        with patch('django_revolution.openapi.generator.run_command') as mock_run_command, \
             patch('django_revolution.openapi.generator.find_manage_py') as mock_find_manage_py:
            mock_run_command.return_value = (True, "Success")
            mock_find_manage_py.return_value = Path("/tmp/manage.py")
            
            schemas = mock_generator.generate_schemas()
            
            # Should use sequential generation when disabled
            assert len(schemas) == 3  # 3 zones
            assert mock_run_command.call_count == 3

    def test_multithreaded_schema_generation(self, mock_generator):
        """Test multithreaded schema generation."""
        mock_generator.config.enable_multithreading = True
        mock_generator.config.max_workers = 2

        with patch('django_revolution.openapi.generator.run_command') as mock_run_command, \
             patch('django_revolution.openapi.generator.find_manage_py') as mock_find_manage_py:
            mock_run_command.return_value = (True, "Success")
            mock_find_manage_py.return_value = Path("/tmp/manage.py")
            
            schemas = mock_generator.generate_schemas()
            
            # Should generate schemas for all zones
            assert len(schemas) == 3
            assert mock_run_command.call_count == 3

    def test_multithreaded_typescript_generation(self, mock_generator):
        """Test multithreaded TypeScript client generation."""
        mock_generator.config.enable_multithreading = True
        mock_generator.config.max_workers = 2
        mock_generator.config.generators.typescript.enabled = True

        # Mock schemas
        schemas = {
            "public": Path("/tmp/public.yaml"),
            "admin": Path("/tmp/admin.yaml"),
            "api": Path("/tmp/api.yaml")
        }

        # Mock TypeScript generator
        mock_generator.ts_generator = Mock()
        mock_generator.ts_generator.generate_client.return_value = Mock(
            success=True,
            zone_name="test",
            output_path=Path("/tmp"),
            files_generated=5,
            error_message=""
        )

        results = mock_generator.generate_typescript_clients(schemas)
        
        # Should generate clients for all schemas
        assert len(results) == 3
        assert mock_generator.ts_generator.generate_client.call_count == 3

    def test_multithreaded_python_generation(self, mock_generator):
        """Test multithreaded Python client generation."""
        mock_generator.config.enable_multithreading = True
        mock_generator.config.max_workers = 2
        mock_generator.config.generators.python.enabled = True

        # Mock schemas
        schemas = {
            "public": Path("/tmp/public.yaml"),
            "admin": Path("/tmp/admin.yaml"),
            "api": Path("/tmp/api.yaml")
        }

        # Mock Python generator
        mock_generator.python_generator = Mock()
        mock_generator.python_generator.generate_client.return_value = Mock(
            success=True,
            zone_name="test",
            output_path=Path("/tmp"),
            files_generated=3,
            error_message=""
        )

        results = mock_generator.generate_python_clients(schemas)
        
        # Should generate clients for all schemas
        assert len(results) == 3
        assert mock_generator.python_generator.generate_client.call_count == 3

    def test_thread_exception_handling(self, mock_generator):
        """Test that thread exceptions are properly handled."""
        mock_generator.config.enable_multithreading = True
        mock_generator.config.max_workers = 2

        with patch('django_revolution.openapi.generator.run_command') as mock_run_command, \
             patch('django_revolution.openapi.generator.find_manage_py') as mock_find_manage_py:
            # Make one call fail
            def mock_run_side_effect(*args, **kwargs):
                if "public" in str(args):
                    return (False, "Error in public zone")
                return (True, "Success")

            mock_run_command.side_effect = mock_run_side_effect
            mock_find_manage_py.return_value = Path("/tmp/manage.py")
            
            schemas = mock_generator.generate_schemas()
            
            # Should handle exceptions gracefully
            assert len(schemas) == 2  # Only successful ones
            assert mock_run_command.call_count == 3

    def test_max_workers_limit(self, mock_generator):
        """Test that max_workers is properly limited."""
        mock_generator.config.enable_multithreading = True
        mock_generator.config.max_workers = 10  # More than zones

        with patch('django_revolution.openapi.generator.run_command') as mock_run_command, \
             patch('django_revolution.openapi.generator.find_manage_py') as mock_find_manage_py:
            mock_run_command.return_value = (True, "Success")
            mock_find_manage_py.return_value = Path("/tmp/manage.py")
            
            schemas = mock_generator.generate_schemas()
            
            # Should limit workers to number of zones
            assert len(schemas) == 3
            assert mock_run_command.call_count == 3

    def test_status_includes_multithreading_info(self, mock_generator):
        """Test that status includes multithreading information."""
        status = mock_generator.get_status()
        
        assert "multithreading" in status
        assert status["multithreading"]["enabled"] is True
        assert status["multithreading"]["max_workers"] == 4
        assert status["multithreading"]["threading_available"] is True

    def test_performance_comparison(self, mock_generator):
        """Test performance comparison between sequential and multithreaded."""
        # Test sequential
        mock_generator.config.enable_multithreading = False
        
        with patch('django_revolution.openapi.generator.run_command') as mock_run_command:
            mock_run_command.return_value = (True, "Success")
            
            start_time = time.time()
            schemas_seq = mock_generator.generate_schemas()
            sequential_time = time.time() - start_time

        # Test multithreaded
        mock_generator.config.enable_multithreading = True
        
        with patch('django_revolution.openapi.generator.run_command') as mock_run_command:
            mock_run_command.return_value = (True, "Success")
            
            start_time = time.time()
            schemas_mt = mock_generator.generate_schemas()
            multithreaded_time = time.time() - start_time

        # Both should generate same number of schemas
        assert len(schemas_seq) == len(schemas_mt)
        
        # Log performance info for manual verification
        print(f"Sequential time: {sequential_time:.3f}s")
        print(f"Multithreaded time: {multithreaded_time:.3f}s")
        if multithreaded_time > 0:
            speedup = sequential_time / multithreaded_time
            print(f"Speedup: {speedup:.2f}x")

    def test_cli_multithreading_options(self):
        """Test CLI multithreading options."""
        from django_revolution.cli import main
        
        # Test with --no-multithreading
        with patch('sys.argv', ['django-revolution', '--no-multithreading', '--status']):
            with patch('django_revolution.cli.handle_status') as mock_handle_status:
                main()
                # Should call handle_status with multithreading disabled
                mock_handle_status.assert_called_once()

        # Test with --max-workers
        with patch('sys.argv', ['django-revolution', '--max-workers', '10', '--status']):
            with patch('django_revolution.cli.handle_status') as mock_handle_status:
                main()
                # Should call handle_status with max_workers=10
                mock_handle_status.assert_called_once()


class TestMultithreadingIntegration:
    """Integration tests for multithreading functionality."""

    def test_full_generation_pipeline_multithreaded(self, tmp_path):
        """Test full generation pipeline with multithreading."""
        config = DjangoRevolutionSettings(
            enable_multithreading=True,
            max_workers=2,
            output=DjangoRevolutionSettings().output,
            output__base_directory=str(tmp_path / "openapi"),
            zones={
                "test1": {
                    "apps": ["django.contrib.auth"],
                    "title": "Test 1",
                    "version": "v1"
                },
                "test2": {
                    "apps": ["django.contrib.contenttypes"],
                    "title": "Test 2", 
                    "version": "v1"
                }
            }
        )

        with patch('django_revolution.openapi.generator.get_django_manage_py') as mock_manage_py:
            mock_manage_py.return_value = tmp_path / "manage.py"
            (tmp_path / "manage.py").write_text("# Mock manage.py")
            
            generator = OpenAPIGenerator(config)
            
            # Mock all external dependencies
            with patch('django_revolution.openapi.generator.run_command') as mock_run_command:
                mock_run_command.return_value = (True, "Success")
                
                with patch.object(generator.zone_manager, 'create_dynamic_urlconf_module') as mock_create_module:
                    mock_create_module.return_value = Mock(__name__="mock_urls")
                    
                    # Test full generation
                    summary = generator.generate_all()
                    
                    # Should complete successfully
                    assert summary.total_zones == 2
                    assert summary.duration_seconds > 0 