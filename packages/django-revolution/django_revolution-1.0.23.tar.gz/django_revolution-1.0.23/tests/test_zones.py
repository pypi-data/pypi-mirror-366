"""
Tests for Django Revolution zones functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock
from pydantic import ValidationError

from django_revolution.config import DjangoRevolutionSettings
from django_revolution.zones import ZoneModel, ZoneManager, ZoneDetector


class TestZoneModel:
    """Test ZoneModel functionality."""

    def test_zone_model_creation(self):
        """Test creating a ZoneModel."""
        zone = ZoneModel(
            name="test_zone",
            apps=["django.contrib.auth", "django.contrib.contenttypes"],
            title="Test Zone",
            description="Test zone description",
            public=True,
            auth_required=False,
            version="v1"
        )
        
        assert zone.name == "test_zone"
        assert zone.apps == ["django.contrib.auth", "django.contrib.contenttypes"]
        assert zone.title == "Test Zone"
        assert zone.description == "Test zone description"
        assert zone.public is True
        assert zone.auth_required is False
        assert zone.version == "v1"
        assert zone.path_prefix == "test"

    def test_zone_model_defaults(self):
        """Test ZoneModel default values."""
        zone = ZoneModel(
            name="test_zone",
            apps=["django.contrib.auth"]
        )
        
        assert zone.name == "test_zone"
        assert zone.apps == ["django.contrib.auth"]
        assert zone.title is None  # Title is not auto-generated anymore
        assert zone.public is True
        assert zone.auth_required is False
        assert zone.version == "v1"
        assert zone.path_prefix == "test_zone"  # Auto-generated from name

    def test_zone_model_validation(self):
        """Test ZoneModel validation."""
        # Test empty apps list
        with pytest.raises(ValidationError):
            ZoneModel(name="test", apps=[])
        
        # Test empty name
        with pytest.raises(ValueError, match="Zone name cannot be empty"):
            ZoneModel(name="", apps=["django.contrib.auth"])
        
        # Test whitespace name
        with pytest.raises(ValueError, match="Zone name cannot be empty"):
            ZoneModel(name="   ", apps=["django.contrib.auth"])

    def test_zone_model_name_normalization(self):
        """Test zone name normalization."""
        zone = ZoneModel(
            name="  TEST_ZONE  ",
            apps=["django.contrib.auth"]
        )
        
        assert zone.name == "test_zone"  # Normalized to lowercase and stripped

    def test_zone_model_post_init(self):
        """Test ZoneModel post-init processing."""
        zone = ZoneModel(
            name="test_zone",
            apps=["django.contrib.auth"]
        )
        
        # Test title (not auto-generated anymore)
        assert zone.title is None
        
        # Test auto-generated path_prefix
        assert zone.path_prefix == "test_zone"

    def test_zone_model_with_custom_prefix(self):
        """Test ZoneModel with custom path prefix."""
        zone = ZoneModel(
            name="test_zone",
            apps=["django.contrib.auth"]
        )
        
        assert zone.path_prefix == "custom_prefix"

    def test_zone_model_with_custom_title(self):
        """Test ZoneModel with custom title."""
        zone = ZoneModel(
            name="test_zone",
            apps=["django.contrib.auth"],
            title="Custom Title"
        )
        
        assert zone.title == "Custom Title"


class TestZoneManager:
    """Test ZoneManager functionality."""

    def test_zone_manager_creation(self):
        """Test creating a ZoneManager."""
        config = DjangoRevolutionSettings(
            zones={
                "public": {
                    "apps": ["django.contrib.auth"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        zone_manager = ZoneManager(config)
        
        assert zone_manager.config == config
        assert len(zone_manager.zones) == 1
        assert "public" in zone_manager.zones
        assert isinstance(zone_manager.zones["public"], ZoneModel)

    def test_zone_manager_empty_zones(self):
        """Test ZoneManager with empty zones."""
        config = DjangoRevolutionSettings(zones={})
        zone_manager = ZoneManager(config)
        
        assert len(zone_manager.zones) == 0

    def test_zone_manager_multiple_zones(self):
        """Test ZoneManager with multiple zones."""
        config = DjangoRevolutionSettings(
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
        
        zone_manager = ZoneManager(config)
        
        assert len(zone_manager.zones) == 2
        assert "public" in zone_manager.zones
        assert "admin" in zone_manager.zones
        assert zone_manager.zones["public"].name == "public"
        assert zone_manager.zones["admin"].name == "admin"

    def test_zone_manager_get_zone(self):
        """Test ZoneManager get_zone method."""
        config = DjangoRevolutionSettings(
            zones={
                "public": {
                    "apps": ["django.contrib.auth"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        zone_manager = ZoneManager(config)
        
        zone = zone_manager.get_zone("public")
        assert zone is not None
        assert isinstance(zone, ZoneModel)
        assert zone.name == "public"
        
        zone = zone_manager.get_zone("nonexistent")
        assert zone is None

    def test_zone_manager_zone_names(self):
        """Test ZoneManager zone names."""
        config = DjangoRevolutionSettings(
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
        
        zone_manager = ZoneManager(config)
        
        zone_names = list(zone_manager.zones.keys())
        assert len(zone_names) == 2
        assert "public" in zone_names
        assert "admin" in zone_names

    def test_zone_manager_validation(self):
        """Test ZoneManager validation."""
        # Test duplicate apps
        config = DjangoRevolutionSettings(
            zones={
                "zone1": {
                    "apps": ["django.contrib.auth"],
                    "title": "Zone 1",
                    "version": "v1"
                },
                "zone2": {
                    "apps": ["django.contrib.auth"],  # Duplicate app
                    "title": "Zone 2",
                    "version": "v1"
                }
            }
        )
        
        with pytest.raises(ValueError, match="Duplicate apps across zones"):
            ZoneManager(config)

    def test_zone_manager_create_dynamic_urlconf_module(self):
        """Test ZoneManager create_dynamic_urlconf_module method."""
        config = DjangoRevolutionSettings(
            zones={
                "public": {
                    "apps": ["django.contrib.auth"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        zone_manager = ZoneManager(config)
        
        # Mock Django apps
        with patch('django.apps.apps.is_installed') as mock_is_installed:
            mock_is_installed.return_value = True
            
            module = zone_manager.create_dynamic_urlconf_module("public", zone_manager.zones["public"])
            
            assert module is not None
            assert hasattr(module, '__name__')

    def test_zone_manager_validate_apps(self):
        """Test ZoneManager app validation."""
        config = DjangoRevolutionSettings(
            zones={
                "public": {
                    "apps": ["django.contrib.auth", "nonexistent.app"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        zone_manager = ZoneManager(config)
        
        # Mock Django apps
        with patch('django.apps.apps.is_installed') as mock_is_installed:
            def mock_is_installed_side_effect(app_name):
                return app_name == "django.contrib.auth"
            
            mock_is_installed.side_effect = mock_is_installed_side_effect
            
            # Should not raise exception for valid apps
            zone_manager.validate_apps()


class TestZoneDetector:
    """Test ZoneDetector functionality."""

    def test_zone_detector_creation(self):
        """Test creating a ZoneDetector."""
        config = DjangoRevolutionSettings(
            zones={
                "public": {
                    "apps": ["django.contrib.auth"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        zone_detector = ZoneDetector(config)
        
        assert zone_detector.config == config
        assert len(zone_detector.zones) == 1

    def test_zone_detector_detect_zones(self):
        """Test ZoneDetector zone detection."""
        config = DjangoRevolutionSettings(
            zones={
                "public": {
                    "apps": ["django.contrib.auth"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        zone_detector = ZoneDetector(config)
        
        # Mock Django apps
        with patch('django.apps.apps.is_installed') as mock_is_installed:
            mock_is_installed.return_value = True
            
            detected_zones = zone_detector.detect_zones()
            
            assert len(detected_zones) == 1
            assert "public" in detected_zones

    def test_zone_detector_detect_zones_with_missing_apps(self):
        """Test ZoneDetector with missing apps."""
        config = DjangoRevolutionSettings(
            zones={
                "public": {
                    "apps": ["django.contrib.auth", "nonexistent.app"],
                    "title": "Public API",
                    "version": "v1"
                }
            }
        )
        
        zone_detector = ZoneDetector(config)
        
        # Mock Django apps
        with patch('django.apps.apps.is_installed') as mock_is_installed:
            def mock_is_installed_side_effect(app_name):
                return app_name == "django.contrib.auth"
            
            mock_is_installed.side_effect = mock_is_installed_side_effect
            
            detected_zones = zone_detector.detect_zones()
            
            # Should only include zones with all apps available
            assert len(detected_zones) == 0

    def test_zone_detector_get_available_zones(self):
        """Test ZoneDetector get_available_zones method."""
        config = DjangoRevolutionSettings(
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
        
        zone_detector = ZoneDetector(config)
        
        # Mock Django apps
        with patch('django.apps.apps.is_installed') as mock_is_installed:
            mock_is_installed.return_value = True
            
            available_zones = zone_detector.get_available_zones()
            
            assert len(available_zones) == 2
            assert "public" in available_zones
            assert "admin" in available_zones

    def test_zone_detector_get_unavailable_zones(self):
        """Test ZoneDetector get_unavailable_zones method."""
        config = DjangoRevolutionSettings(
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
        
        zone_detector = ZoneDetector(config)
        
        # Mock Django apps
        with patch('django.apps.apps.is_installed') as mock_is_installed:
            def mock_is_installed_side_effect(app_name):
                return app_name == "django.contrib.auth"
            
            mock_is_installed.side_effect = mock_is_installed_side_effect
            
            unavailable_zones = zone_detector.get_unavailable_zones()
            
            assert len(unavailable_zones) == 1
            assert "admin" in unavailable_zones