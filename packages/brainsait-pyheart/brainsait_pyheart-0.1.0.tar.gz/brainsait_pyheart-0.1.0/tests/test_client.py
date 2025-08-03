"""Tests for FHIR client."""

import pytest
from unittest.mock import Mock, patch
from pyheart.core.client import FHIRClient, ClientConfig


def test_client_config():
    """Test client configuration."""
    config = ClientConfig(
        base_url="https://fhir.example.com",
        auth_token="test_token",
        timeout=60
    )
    
    assert str(config.base_url) == "https://fhir.example.com/"
    assert config.auth_token == "test_token"
    assert config.timeout == 60


def test_fhir_client_initialization():
    """Test FHIR client initialization."""
    client = FHIRClient("https://fhir.example.com")
    assert str(client.config.base_url) == "https://fhir.example.com/"


@patch('httpx.Client')
def test_get_patient_headers(mock_client_class):
    """Test FHIR client headers."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    config = ClientConfig(
        base_url="https://fhir.example.com",
        auth_token="test_token"
    )
    client = FHIRClient(config)
    
    headers = client._get_headers()
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_token"
    assert headers["Accept"] == "application/fhir+json"


@patch('httpx.Client')
def test_search_resources(mock_client_class):
    """Test resource search."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "resourceType": "Bundle",
        "total": 1,
        "entry": [{"resource": {"resourceType": "Patient", "id": "123"}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_client.get.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    client = FHIRClient("https://fhir.example.com")
    result = client.search("Patient", {"family": "Smith"})
    
    assert result["resourceType"] == "Bundle"
    assert result["total"] == 1
    mock_client.get.assert_called_once()


@patch('httpx.Client')
def test_create_resource(mock_client_class):
    """Test resource creation."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "resourceType": "Patient",
        "id": "123",
        "name": [{"family": "Doe", "given": ["John"]}]
    }
    mock_response.raise_for_status.return_value = None
    mock_client.post.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    client = FHIRClient("https://fhir.example.com")
    patient_data = {
        "resourceType": "Patient",
        "name": [{"family": "Doe", "given": ["John"]}]
    }
    
    result = client.create(patient_data)
    
    assert result["resourceType"] == "Patient"
    assert result["id"] == "123"
    mock_client.post.assert_called_once()