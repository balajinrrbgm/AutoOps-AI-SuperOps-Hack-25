"""
Unit tests for SuperOps Client
"""
import pytest
from unittest.mock import Mock, patch
from src.integrations.superops_client import SuperOpsClient

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv('SUPEROPS_API_TOKEN', 'test_token')
    monkeypatch.setenv('SUPEROPS_SUBDOMAIN', 'test_subdomain')
    monkeypatch.setenv('SUPEROPS_DATA_CENTER', 'us')

def test_client_initialization(mock_env):
    client = SuperOpsClient()
    assert client.api_token == 'test_token'
    assert client.subdomain == 'test_subdomain'
    assert 'api.superops.ai' in client.base_url

@patch('src.integrations.superops_client.Client')
def test_get_device_inventory(mock_client, mock_env):
    client = SuperOpsClient()
    mock_client.return_value.execute.return_value = {
        'devices': [
            {'id': '1', 'name': 'test-device'}
        ]
    }

    devices = client.get_device_inventory()
    assert len(devices) == 1
    assert devices[0]['name'] == 'test-device'

@patch('src.integrations.superops_client.Client')
def test_get_patch_status(mock_client, mock_env):
    client = SuperOpsClient()
    mock_client.return_value.execute.return_value = {
        'patchStatus': [
            {
                'deviceId': '1',
                'pendingPatches': 5,
                'complianceStatus': 'NON_COMPLIANT'
            }
        ]
    }

    status = client.get_patch_status(['1'])
    assert len(status) == 1
    assert status[0]['pendingPatches'] == 5
