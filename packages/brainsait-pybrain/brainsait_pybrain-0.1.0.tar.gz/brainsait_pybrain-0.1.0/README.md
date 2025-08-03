# 🧠 PyBrain - Unified Healthcare Intelligence Platform

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pybrain.svg)](https://pypi.org/project/pybrain/)

PyBrain is the intelligence layer of the BrainSAIT Healthcare Unification Platform, providing AI-powered data harmonization, clinical NLP, and decision support for building next-generation healthcare systems.

## 🚀 Features

- **AI-Powered Data Harmonization**: Automatically maps and transforms data across different healthcare standards
- **Clinical NLP Engine**: Extracts structured data from unstructured clinical notes with medical language understanding
- **Federated Learning Framework**: Enables privacy-preserving AI model training across healthcare institutions
- **Real-time Decision Support**: Provides evidence-based recommendations using ensemble AI models
- **Predictive Analytics**: Forecasts patient outcomes, resource needs, and population health trends

## 📦 Installation

```bash
pip install pybrain
```

For development:
```bash
pip install pybrain[dev]
```

For all ML features:
```bash
pip install pybrain[ml,nlp]
```

## 🔧 Quick Start

### Basic Usage

```python
from pybrain import AIEngine, DataHarmonizer

# Initialize AI engine
ai = AIEngine()

# Extract entities from clinical text
clinical_note = "Patient presents with type 2 diabetes, prescribed metformin 500mg twice daily"
entities = ai.extract_clinical_entities(clinical_note)
print(entities)
# {'conditions': ['Diabetes'], 'medications': ['Metformin'], ...}

# Harmonize HL7v2 data to FHIR
harmonizer = DataHarmonizer()
hl7_data = {
    "PID": {
        "5": {"1": "Smith", "2": "John"},
        "7": "19800415",
        "8": "M"
    }
}
fhir_patient = harmonizer.harmonize_to_fhir(hl7_data, "hl7v2", "Patient")
```

### AI-Powered Risk Assessment

```python
from pybrain import AIEngine, DecisionEngine

ai = AIEngine()
decision_engine = DecisionEngine()

# Patient data
patient_data = {
    "age": 65,
    "conditions": ["diabetes", "hypertension"],
    "medications": ["metformin", "lisinopril"],
    "bmi": 28.5
}

# Predict clinical risks
risk_score = ai.predict_risk_score(patient_data)
print(f"Overall risk score: {risk_score:.2f}")

# Get clinical recommendations
recommendations = decision_engine.evaluate_patient(patient_data)
print("Clinical alerts:", recommendations["alerts"])
```

### Population Health Analytics

```python
from pybrain import AnalyticsEngine

analytics = AnalyticsEngine()

# Analyze population trends
population_data = [
    {"patient": {"id": "1", "birthDate": "1960-01-01"}, "observations": [...]},
    {"patient": {"id": "2", "birthDate": "1975-05-15"}, "observations": [...]}
]

metrics = analytics.calculate_population_metrics(population_data)
print(f"High-risk patients: {metrics['risk_distribution']['high']}")
print(f"Recommendations: {metrics['recommendations']}")
```

### CLI Usage

```bash
# Analyze clinical text
pybrain analyze -t "Patient has hypertension and diabetes"

# Harmonize data files
pybrain harmonize -i patient.json -f hl7v2 -r Patient -o patient_fhir.json

# Start API server
pybrain serve --port 8000
```

## 🏗️ Architecture

PyBrain is designed as a modular, scalable platform:

```
pybrain/
├── core/
│   ├── ai/          # AI models and engines
│   ├── harmonizer/  # Data harmonization
│   ├── analytics/   # Analytics engine
│   ├── decision/    # Decision support
│   └── knowledge/   # Knowledge graphs
├── connectors/      # External system connectors
├── models/          # Pre-trained models
└── utils/          # Utilities
```

## 🤝 Integration with PyHeart

PyBrain works seamlessly with PyHeart for complete healthcare system unification:

```python
from pybrain import AIEngine
from pyheart import FHIRClient

# Use PyHeart for data access
client = FHIRClient("https://fhir.example.com")
patient_data = client.get_patient("12345")

# Use PyBrain for intelligence
ai = AIEngine()
risk_score = ai.predict_risk_score(patient_data)

if risk_score > 0.8:
    print("High-risk patient - immediate intervention required")
```

## 🧪 Key Capabilities

### Clinical NLP
- Medical entity extraction
- Clinical concept normalization
- FHIR-compliant text processing
- Multi-language support

### AI-Powered Analytics
- Risk stratification
- Readmission prediction
- Fall risk assessment
- Medication adherence prediction

### Data Harmonization
- HL7v2 to FHIR transformation
- Custom EHR format mapping
- Terminology services integration
- Quality validation

### Decision Support
- Clinical rule engine
- Evidence-based recommendations
- Drug interaction checking
- Population health insights

## 📚 Documentation

Full documentation available at: https://pybrain.readthedocs.io

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=pybrain
```

## 🤝 Contributing

We welcome contributions! Please see our Contributing Guide for details.

## 📄 License

PyBrain is licensed under the Apache License 2.0. See LICENSE for details.

## 🌟 Acknowledgments

Built with ❤️ by the BrainSAIT Healthcare Innovation Lab

Special thanks to the open-source healthcare community and all contributors.

---

**Together with PyHeart, PyBrain is building the future of intelligent healthcare.**