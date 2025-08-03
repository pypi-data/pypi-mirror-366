"""
PyHeart - Healthcare Interoperability & Workflow Engine

Universal integration platform for seamless healthcare system connectivity,
workflow orchestration, and secure data exchange.
"""

__version__ = "0.1.0"
__author__ = "BrainSAIT Healthcare Innovation Lab"
__email__ = "healthcare@brainsait.com"

from pyheart.core.client import FHIRClient, HealthcareClient
from pyheart.core.server import FHIRServer, APIGateway
from pyheart.core.workflow import WorkflowEngine, ProcessDefinition
from pyheart.core.integration import IntegrationHub, Adapter
from pyheart.core.security import SecurityManager, AuthProvider

__all__ = [
    "FHIRClient",
    "HealthcareClient",
    "FHIRServer",
    "APIGateway",
    "WorkflowEngine",
    "ProcessDefinition",
    "IntegrationHub",
    "Adapter",
    "SecurityManager",
    "AuthProvider",
]

# Configure structured logging
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)