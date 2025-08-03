# ❤️ PyHeart - Healthcare Interoperability & Workflow Engine

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pyheart.svg)](https://pypi.org/project/pyheart/)

PyHeart is the integration layer of the BrainSAIT Healthcare Unification Platform, providing universal healthcare system connectivity, workflow orchestration, and secure data exchange.

## 🚀 Features

- **Universal API Gateway**: Single interface for all healthcare system integrations
- **Event-Driven Architecture**: Real-time data streaming and processing
- **Microservices Framework**: Modular, scalable healthcare services
- **Security & Compliance Engine**: HIPAA, GDPR, and regional compliance automation
- **Workflow Orchestration**: Complex healthcare process automation

## 📦 Installation

```bash
pip install pyheart
```

For development:
```bash
pip install pyheart[dev]
```

For legacy system support:
```bash
pip install pyheart[legacy]
```

## 🔧 Quick Start

### FHIR Client Usage

```python
from pyheart import FHIRClient

# Connect to FHIR server
client = FHIRClient("https://fhir.example.com")

# Get patient
patient = client.get_patient("12345")
print(f"Patient: {patient}")

# Search patients
bundle = client.search("Patient", {"family": "Smith", "birthdate": "ge1970"})
for entry in bundle.get("entry", []):
    print(f"Found: {entry['resource']['id']}")

# Create patient
new_patient = {
    "resourceType": "Patient",
    "name": [{"given": ["John"], "family": "Doe"}],
    "gender": "male",
    "birthDate": "1990-01-01"
}
created = client.create(new_patient)
```

### Workflow Engine

```python
from pyheart import WorkflowEngine, ProcessDefinition, Task

# Define a clinical process
process = ProcessDefinition(
    id="medication-reconciliation",
    name="Medication Reconciliation Process",
    tasks=[
        Task(
            id="fetch-current-meds",
            name="Fetch Current Medications",
            type="api_call",
            config={
                "url": "${fhir_server}/MedicationRequest?patient=${patient_id}",
                "method": "GET"
            }
        ),
        Task(
            id="analyze-interactions",
            name="Analyze Drug Interactions",
            type="transformation",
            dependencies=["fetch-current-meds"],
            config={
                "transform": {"type": "drug_interaction_check"}
            }
        )
    ]
)

# Execute workflow
engine = WorkflowEngine()
engine.register_process(process)

instance_id = await engine.start_process(
    "medication-reconciliation",
    {"patient_id": "12345", "physician_email": "dr.smith@example.com"}
)
```

### Healthcare System Integration

```python
from pyheart import IntegrationHub, FHIRAdapter, HL7Adapter

# Setup integration hub
hub = IntegrationHub()

# Register adapters for different systems
hub.register_adapter("hospital_a", FHIRAdapter("hospital_a"))
hub.register_adapter("lab_system", HL7Adapter("lab_system"))

# Connect to systems
await hub.connect_system("hospital_a", {"base_url": "https://hospital-a.com/fhir"})
await hub.connect_system("lab_system", {"host": "lab.hospital.com", "port": 2575})

# Fetch data from all systems
patient_data = await hub.fetch_from_all_systems("Patient", {"id": "12345"})
```

### CLI Usage

```bash
# FHIR operations
pyheart fhir -s https://fhir.example.com -r Patient -i 12345
pyheart fhir -s https://fhir.example.com -r Observation -q '{"patient": "12345"}'

# Run workflows
pyheart workflow -f medication-check.json -v '{"patient_id": "12345"}'

# Start server
pyheart serve --port 8000

# Sync data between systems
pyheart sync -s https://old.example.com -t https://new.example.com -r Patient

# System diagnostics
pyheart doctor
```

## 🏗️ Architecture

PyHeart provides a layered architecture for healthcare integration:

```
pyheart/
├── core/
│   ├── client/      # FHIR and legacy clients
│   ├── server/      # API gateway and FHIR server
│   ├── workflow/    # Process orchestration
│   ├── integration/ # System adapters
│   └── security/    # Auth and encryption
├── adapters/        # Legacy system adapters
├── messaging/       # Event streaming
└── api/            # REST/GraphQL APIs
```

## 🤝 Integration with PyBrain

PyHeart and PyBrain work together seamlessly:

```python
from pyheart import FHIRClient, WorkflowEngine
from pybrain import AIEngine, DataHarmonizer

# Use PyHeart for data access
client = FHIRClient("https://fhir.example.com")
observations = client.search("Observation", {"patient": "12345"})

# Use PyBrain for intelligence
ai = AIEngine()
harmonizer = DataHarmonizer()

# Process observations with AI
for entry in observations.get("entry", []):
    obs = entry["resource"]
    
    # Harmonize if needed
    if obs.get("meta", {}).get("source") != "unified":
        obs = harmonizer.harmonize_to_fhir(obs, "custom", "Observation")
    
    # AI analysis
    risk = ai.predict_risk_score({"patient_id": "12345"})
    
    # Trigger workflow if high risk
    if risk > 0.8:
        engine = WorkflowEngine()
        await engine.start_process("high-risk-intervention", {
            "patient_id": "12345",
            "risk_score": risk
        })
```

## 🔒 Security & Compliance

PyHeart includes comprehensive security features:

```python
from pyheart import SecurityManager, AuthProvider

# Configure security
security = SecurityManager()
security.enable_encryption("AES-256-GCM")
security.enable_audit_logging()
security.configure_compliance(["HIPAA", "GDPR"])

# OAuth2/SMART on FHIR authentication
auth = AuthProvider("oauth2")
token = await auth.get_token(
    client_id="app-123",
    scope="patient/*.read launch"
)

# Use authenticated client
client = FHIRClient(
    base_url="https://fhir.example.com",
    auth_token=token
)
```

## 🌟 Advanced Features

### Multi-System Client
```python
from pyheart import HealthcareClient

# Query multiple systems simultaneously
client = HealthcareClient()
client.add_fhir_system("hospital_a", FHIRClient("https://a.example.com"))
client.add_fhir_system("hospital_b", FHIRClient("https://b.example.com"))

# Unified patient record
unified_patient = await client.get_unified_patient("12345")
```

### Workflow Orchestration
- Visual workflow designer compatible
- Event-driven triggers
- Human task management
- Error handling and retries
- Parallel and sequential execution

### Legacy System Support
- HL7v2 messaging
- DICOM integration
- X12 transactions
- Custom adapter framework

## 📚 Documentation

Full documentation available at: https://pyheart.readthedocs.io

### Quick Links
- API Reference
- Workflow Guide
- Integration Patterns
- Security Best Practices

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=pyheart

# Integration tests
pytest tests/integration --integration
```

## 🚀 Deployment

### Docker
```bash
docker run -p 8000:8000 brainsait/pyheart:latest
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pyheart
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pyheart
  template:
    spec:
      containers:
      - name: pyheart
        image: brainsait/pyheart:latest
        ports:
        - containerPort: 8000
```

## 🤝 Contributing

We welcome contributions! Please see our Contributing Guide for details.

## 📄 License

PyHeart is licensed under the Apache License 2.0. See LICENSE for details.

## 🌟 Acknowledgments

Built with ❤️ by the BrainSAIT Healthcare Innovation Lab

Special thanks to:
- The FHIR community for excellent standards
- FastAPI for the amazing web framework
- All our contributors and users

---

**Together with PyBrain, PyHeart is building the future of connected healthcare.**