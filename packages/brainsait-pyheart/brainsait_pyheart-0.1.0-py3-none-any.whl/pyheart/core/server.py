"""
FHIR Server and API Gateway implementation
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import structlog

logger = structlog.get_logger()


class FHIRServer:
    """
    FHIR server implementation
    """
    
    def __init__(self, app: Optional[FastAPI] = None):
        self.app = app or FastAPI(title="PyHeart FHIR Server")
        self.resources: Dict[str, Dict[str, Any]] = {}
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup FHIR REST API routes"""
        
        @self.app.get("/metadata")
        async def get_capability_statement():
            """Get FHIR capability statement"""
            return {
                "resourceType": "CapabilityStatement",
                "status": "active",
                "date": "2024-01-01",
                "publisher": "PyHeart",
                "kind": "instance",
                "software": {
                    "name": "PyHeart FHIR Server",
                    "version": "0.1.0"
                },
                "fhirVersion": "4.0.1",
                "format": ["application/fhir+json"],
                "rest": [{
                    "mode": "server",
                    "resource": [
                        {
                            "type": "Patient",
                            "interaction": [
                                {"code": "read"},
                                {"code": "create"},
                                {"code": "update"},
                                {"code": "delete"},
                                {"code": "search-type"}
                            ]
                        }
                    ]
                }]
            }
        
        @self.app.get("/{resource_type}/{resource_id}")
        async def read_resource(resource_type: str, resource_id: str):
            """Read a specific resource"""
            if resource_type not in self.resources:
                raise HTTPException(status_code=404, detail="Resource type not found")
            
            if resource_id not in self.resources[resource_type]:
                raise HTTPException(status_code=404, detail="Resource not found")
            
            return self.resources[resource_type][resource_id]
        
        @self.app.post("/{resource_type}")
        async def create_resource(resource_type: str, resource: Dict[str, Any]):
            """Create a new resource"""
            if resource_type not in self.resources:
                self.resources[resource_type] = {}
            
            # Generate ID if not provided
            if "id" not in resource:
                resource["id"] = f"{len(self.resources[resource_type]) + 1}"
            
            self.resources[resource_type][resource["id"]] = resource
            return resource
        
        @self.app.get("/{resource_type}")
        async def search_resources(resource_type: str):
            """Search resources"""
            if resource_type not in self.resources:
                return {
                    "resourceType": "Bundle",
                    "type": "searchset",
                    "total": 0,
                    "entry": []
                }
            
            entries = []
            for resource in self.resources[resource_type].values():
                entries.append({
                    "resource": resource
                })
            
            return {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": len(entries),
                "entry": entries
            }


class APIGateway:
    """
    API Gateway for healthcare system integration
    """
    
    def __init__(self):
        self.app = FastAPI(title="PyHeart API Gateway")
        self.routes: Dict[str, Any] = {}
        self._setup_gateway_routes()
    
    def _setup_gateway_routes(self):
        """Setup API gateway routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "service": "PyHeart API Gateway"}
        
        @self.app.get("/systems")
        async def list_systems():
            """List connected healthcare systems"""
            return {"systems": list(self.routes.keys())}
        
        @self.app.post("/systems/{system_id}/proxy")
        async def proxy_request(system_id: str, request_data: Dict[str, Any]):
            """Proxy request to healthcare system"""
            if system_id not in self.routes:
                raise HTTPException(status_code=404, detail="System not found")
            
            # Simplified proxy logic
            logger.info("Proxying request", system_id=system_id)
            return {"proxied": True, "system": system_id, "data": request_data}
    
    def register_system(self, system_id: str, config: Dict[str, Any]):
        """Register a healthcare system"""
        self.routes[system_id] = config
        logger.info("Registered system", system_id=system_id)