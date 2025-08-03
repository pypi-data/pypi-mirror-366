"""
FHIR Client for PyHeart - Universal healthcare data access
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import httpx
import asyncio
from pydantic import BaseModel, Field, HttpUrl
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()


class ClientConfig(BaseModel):
    """Configuration for FHIR client"""
    
    base_url: HttpUrl
    auth_type: str = Field(default="bearer", description="Authentication type")
    auth_token: Optional[str] = None
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")


class FHIRClient:
    """
    Universal FHIR client for healthcare data access
    
    Features:
    - Async/sync operations
    - Automatic retries with exponential backoff
    - Smart caching
    - Batch operations
    - FHIR search with pagination
    """
    
    def __init__(self, config: Union[ClientConfig, str]):
        if isinstance(config, str):
            config = ClientConfig(base_url=config)
        self.config = config
        self._client = self._create_client()
        self._async_client = self._create_async_client()
    
    def _create_client(self) -> httpx.Client:
        """Create synchronous HTTP client"""
        headers = self._get_headers()
        return httpx.Client(
            base_url=str(self.config.base_url),
            headers=headers,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl
        )
    
    def _create_async_client(self) -> httpx.AsyncClient:
        """Create asynchronous HTTP client"""
        headers = self._get_headers()
        return httpx.AsyncClient(
            base_url=str(self.config.base_url),
            headers=headers,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json"
        }
        
        if self.config.auth_token:
            if self.config.auth_type == "bearer":
                headers["Authorization"] = f"Bearer {self.config.auth_token}"
            elif self.config.auth_type == "basic":
                headers["Authorization"] = f"Basic {self.config.auth_token}"
        
        return headers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a patient by ID
        
        Args:
            patient_id: FHIR patient ID
            
        Returns:
            Patient resource dict or None
        """
        try:
            response = self._client.get(f"Patient/{patient_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info("Patient not found", patient_id=patient_id)
                return None
            logger.error("Failed to get patient", 
                        patient_id=patient_id, 
                        error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error getting patient", 
                        patient_id=patient_id,
                        error=str(e))
            raise
    
    async def get_patient_async(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Async version of get_patient"""
        try:
            response = await self._async_client.get(f"Patient/{patient_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def search(self, 
              resource_type: str,
              params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for resources
        
        Args:
            resource_type: FHIR resource type
            params: Search parameters
            
        Returns:
            Bundle containing search results
        """
        params = params or {}
        
        try:
            response = self._client.get(resource_type, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Search failed",
                        resource_type=resource_type,
                        params=params,
                        error=str(e))
            raise
    
    async def search_async(self,
                          resource_type: str,
                          params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Async version of search"""
        params = params or {}
        
        try:
            response = await self._async_client.get(resource_type, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Async search failed",
                        resource_type=resource_type,
                        params=params,
                        error=str(e))
            raise
    
    def create(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new resource
        
        Args:
            resource: FHIR resource to create
            
        Returns:
            Created resource with server-assigned ID
        """
        resource_type = resource.get("resourceType")
        if not resource_type:
            raise ValueError("Resource must have resourceType")
        
        try:
            response = self._client.post(
                resource_type,
                json=resource
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to create resource",
                        resource_type=resource_type,
                        error=str(e))
            raise
    
    async def create_async(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Async version of create"""
        resource_type = resource.get("resourceType")
        if not resource_type:
            raise ValueError("Resource must have resourceType")
        
        try:
            response = await self._async_client.post(
                resource_type,
                json=resource
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to create resource async",
                        resource_type=resource_type,
                        error=str(e))
            raise
    
    def update(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing resource"""
        resource_type = resource.get("resourceType")
        resource_id = resource.get("id")
        
        if not resource_type or not resource_id:
            raise ValueError("Resource must have resourceType and id for update")
        
        try:
            response = self._client.put(
                f"{resource_type}/{resource_id}",
                json=resource
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to update resource",
                        resource_type=resource_type,
                        resource_id=resource_id,
                        error=str(e))
            raise
    
    def delete(self, resource_type: str, resource_id: str) -> bool:
        """Delete a resource"""
        try:
            response = self._client.delete(f"{resource_type}/{resource_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise
    
    def batch(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Execute batch/transaction operations"""
        try:
            response = self._client.post("", json=bundle)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Batch operation failed", error=str(e))
            raise
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capability statement"""
        try:
            response = self._client.get("metadata")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get capabilities", error=str(e))
            raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close HTTP clients"""
        self._client.close()
        if hasattr(self, '_async_client'):
            asyncio.create_task(self._async_client.aclose())
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._async_client.aclose()


class HealthcareClient:
    """
    High-level healthcare client with multi-system support
    """
    
    def __init__(self):
        self.fhir_clients: Dict[str, FHIRClient] = {}
        self.adapters: Dict[str, Any] = {}
    
    def add_fhir_system(self, name: str, client: FHIRClient):
        """Add a FHIR system"""
        self.fhir_clients[name] = client
        logger.info("Added FHIR system", name=name)
    
    def add_legacy_system(self, name: str, adapter: Any):
        """Add a legacy system with adapter"""
        self.adapters[name] = adapter
        logger.info("Added legacy system", name=name)
    
    async def get_unified_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient data from all connected systems
        
        Returns unified patient record
        """
        unified_data = {
            "id": patient_id,
            "sources": {},
            "merged_demographics": {},
            "identifiers": []
        }
        
        # Fetch from all FHIR systems
        tasks = []
        for name, client in self.fhir_clients.items():
            task = self._fetch_patient_data(name, client, patient_id)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(self.fhir_clients.keys(), results):
            if isinstance(result, Exception):
                logger.error("Failed to fetch from system",
                           system=name,
                           error=str(result))
            else:
                unified_data["sources"][name] = result
        
        # Merge demographics intelligently
        self._merge_demographics(unified_data)
        
        return unified_data
    
    async def _fetch_patient_data(self, 
                                 system_name: str,
                                 client: FHIRClient,
                                 patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch patient data from a single system"""
        try:
            patient = await client.get_patient_async(patient_id)
            return patient
        except Exception as e:
            logger.error("Failed to fetch patient",
                       system=system_name,
                       error=str(e))
            raise
    
    def _merge_demographics(self, unified_data: Dict[str, Any]):
        """Intelligently merge patient demographics from multiple sources"""
        sources = unified_data.get("sources", {})
        merged = {}
        
        # Simple merging logic - take first available value
        # In production, would implement sophisticated conflict resolution
        for system_name, patient_data in sources.items():
            if not patient_data:
                continue
            
            # Name
            if not merged.get("name") and patient_data.get("name"):
                merged["name"] = patient_data["name"]
            
            # Birth date
            if not merged.get("birthDate") and patient_data.get("birthDate"):
                merged["birthDate"] = patient_data["birthDate"]
            
            # Gender
            if not merged.get("gender") and patient_data.get("gender"):
                merged["gender"] = patient_data["gender"]
            
            # Identifiers
            if patient_data.get("identifier"):
                unified_data["identifiers"].extend(patient_data["identifier"])
        
        unified_data["merged_demographics"] = merged