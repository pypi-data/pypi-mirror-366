import sys
from unittest.mock import MagicMock

import pytest

from regscale.core.app.application import Application
from regscale.integrations.integration_override import IntegrationOverride


@pytest.fixture()
def config():
    return {
        "findingFromMapping": {
            "tenable_sc": {
                "severity": "risk_level",
                "description": "details",
                "remediation": "rando",
                "title": "default",
            }
        }
    }


def test_integration_mapping_load(config):
    # Mock Application object and its config
    app = Application()
    # Override the config for testing purposes
    app.config = config
    assert "findingFromMapping" in app.config
    # Initialize IntegrationMapping with the mocked app
    integration_mapping = IntegrationOverride(app)
    # Test default
    assert integration_mapping.mapping_exists("tenable_sc", "title") is False

    # Test loading existing mapping
    assert integration_mapping.load("tenable_sc", "severity") == "risk_level"
    assert integration_mapping.load("tenable_sc", "description") == "details"
    assert integration_mapping.load("tenable_sc", "remediation") == "rando"

    # Test loading non-existing mapping
    assert integration_mapping.load("tenable_sc", "title") is None  # default is None
    assert integration_mapping.load("tenable_sc", "non_existing_field") is None
    assert integration_mapping.load("non_existing_integration", "severity") is None
    # Uber fail
    assert integration_mapping.load(None, None) is None


def test_no_config():
    mock_app = MagicMock()
    mock_app.config = {}
    integration_mapping = IntegrationOverride(mock_app)
    assert integration_mapping.load("tenable_sc", "remediation") is None
    assert integration_mapping.load(None, None) is None


def test_singleton():
    app = Application()
    instance1 = IntegrationOverride(app)
    instance2 = IntegrationOverride(app)
    assert instance1 is instance2
