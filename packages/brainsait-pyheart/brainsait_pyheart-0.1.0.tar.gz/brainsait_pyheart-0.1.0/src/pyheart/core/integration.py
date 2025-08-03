"""
Integration Hub and Adapters for healthcare systems
"""

from typing import Any, Dict, List, Optional, Protocol
from abc import ABC, abstractmethod
import structlog

logger = structlog.get_logger()


class Adapter(Protocol):
    """Protocol for healthcare system adapters"""
    
    @abstractmethod
    async def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to the healthcare system"""
        ...
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the healthcare system"""
        ...
    
    @abstractmethod
    async def fetch_data(self, resource_type: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch data from the healthcare system"""
        ...
    
    @abstractmethod
    async def send_data(self, resource_type: str, data: Dict[str, Any]) -> bool:
        """Send data to the healthcare system"""
        ...


class BaseAdapter(ABC):
    """Base adapter implementation"""
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        self.connected = False
        self.config: Dict[str, Any] = {}
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to the healthcare system"""
        self.config = config
        self.connected = True
        logger.info("Connected to system", system_id=self.system_id)
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from the healthcare system"""
        self.connected = False
        logger.info("Disconnected from system", system_id=self.system_id)
        return True


class FHIRAdapter(BaseAdapter):
    """FHIR system adapter"""
    
    async def fetch_data(self, resource_type: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch FHIR data"""
        logger.info("Fetching FHIR data", 
                   system_id=self.system_id,
                   resource_type=resource_type)
        
        # Simplified FHIR fetch
        return [{
            "resourceType": resource_type,
            "id": "example-1",
            "source": self.system_id
        }]
    
    async def send_data(self, resource_type: str, data: Dict[str, Any]) -> bool:
        """Send FHIR data"""
        logger.info("Sending FHIR data",
                   system_id=self.system_id,
                   resource_type=resource_type)
        return True


class HL7Adapter(BaseAdapter):
    """HL7v2 system adapter"""
    
    async def fetch_data(self, resource_type: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch HL7 data"""
        logger.info("Fetching HL7 data",
                   system_id=self.system_id,
                   resource_type=resource_type)
        
        # Simplified HL7 fetch - would parse actual HL7 messages
        return [{
            "message_type": "ADT^A01",
            "patient_id": "12345",
            "source": self.system_id
        }]
    
    async def send_data(self, resource_type: str, data: Dict[str, Any]) -> bool:
        """Send HL7 data"""
        logger.info("Sending HL7 data",
                   system_id=self.system_id,
                   resource_type=resource_type)
        return True


class DICOMAdapter(BaseAdapter):
    """DICOM system adapter"""
    
    async def fetch_data(self, resource_type: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch DICOM data"""
        logger.info("Fetching DICOM data",
                   system_id=self.system_id,
                   resource_type=resource_type)
        
        return [{
            "study_id": "1.2.3.4.5",
            "modality": "CT",
            "source": self.system_id
        }]
    
    async def send_data(self, resource_type: str, data: Dict[str, Any]) -> bool:
        """Send DICOM data"""
        logger.info("Sending DICOM data",
                   system_id=self.system_id,
                   resource_type=resource_type)
        return True


class IntegrationHub:
    """
    Central hub for managing healthcare system integrations
    """
    
    def __init__(self):
        self.adapters: Dict[str, Adapter] = {}
        self.system_configs: Dict[str, Dict[str, Any]] = {}
    
    def register_adapter(self, system_id: str, adapter: Adapter):
        """Register a system adapter"""
        self.adapters[system_id] = adapter
        logger.info("Registered adapter", system_id=system_id)
    
    async def connect_system(self, system_id: str, config: Dict[str, Any]) -> bool:
        """Connect to a healthcare system"""
        if system_id not in self.adapters:
            logger.error("Adapter not found", system_id=system_id)
            return False
        
        adapter = self.adapters[system_id]
        success = await adapter.connect(config)
        
        if success:
            self.system_configs[system_id] = config
        
        return success
    
    async def disconnect_system(self, system_id: str) -> bool:
        """Disconnect from a healthcare system"""
        if system_id not in self.adapters:
            return False
        
        adapter = self.adapters[system_id]
        success = await adapter.disconnect()
        
        if success and system_id in self.system_configs:
            del self.system_configs[system_id]
        
        return success
    
    async def fetch_from_system(self, 
                               system_id: str,
                               resource_type: str,
                               params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch data from a specific system"""
        if system_id not in self.adapters:
            logger.error("System not connected", system_id=system_id)
            return []
        
        adapter = self.adapters[system_id]
        return await adapter.fetch_data(resource_type, params or {})
    
    async def send_to_system(self,
                            system_id: str,
                            resource_type: str,
                            data: Dict[str, Any]) -> bool:
        """Send data to a specific system"""
        if system_id not in self.adapters:
            logger.error("System not connected", system_id=system_id)
            return False
        
        adapter = self.adapters[system_id]
        return await adapter.send_data(resource_type, data)
    
    async def broadcast_data(self,
                           resource_type: str,
                           data: Dict[str, Any],
                           exclude_systems: Optional[List[str]] = None) -> Dict[str, bool]:
        """Broadcast data to all connected systems"""
        exclude_systems = exclude_systems or []
        results = {}
        
        for system_id, adapter in self.adapters.items():
            if system_id in exclude_systems:
                continue
            
            try:
                success = await adapter.send_data(resource_type, data)
                results[system_id] = success
            except Exception as e:
                logger.error("Failed to send to system",
                           system_id=system_id,
                           error=str(e))
                results[system_id] = False
        
        return results
    
    async def fetch_from_all_systems(self,
                                   resource_type: str,
                                   params: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch data from all connected systems"""
        results = {}
        
        for system_id, adapter in self.adapters.items():
            try:
                data = await adapter.fetch_data(resource_type, params or {})
                results[system_id] = data
            except Exception as e:
                logger.error("Failed to fetch from system",
                           system_id=system_id,
                           error=str(e))
                results[system_id] = []
        
        return results
    
    def get_connected_systems(self) -> List[str]:
        """Get list of connected systems"""
        return list(self.system_configs.keys())
    
    def get_system_status(self, system_id: str) -> Dict[str, Any]:
        """Get status of a specific system"""
        if system_id not in self.adapters:
            return {"status": "not_registered"}
        
        adapter = self.adapters[system_id]
        return {
            "status": "connected" if hasattr(adapter, 'connected') and adapter.connected else "disconnected",
            "system_id": system_id,
            "config": self.system_configs.get(system_id, {})
        }