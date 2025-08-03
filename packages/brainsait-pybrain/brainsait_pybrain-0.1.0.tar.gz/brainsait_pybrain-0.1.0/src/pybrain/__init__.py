"""
PyBrain - Unified Healthcare Intelligence Platform

AI-powered healthcare data harmonization, clinical NLP, and decision support
for building the next generation of intelligent healthcare systems.
"""

__version__ = "0.1.0"
__author__ = "BrainSAIT Healthcare Innovation Lab"
__email__ = "healthcare@brainsait.com"

from pybrain.core.ai import AIEngine, ModelRegistry
from pybrain.core.analytics import AnalyticsEngine, HealthMetrics
from pybrain.core.decision import DecisionEngine, ClinicalRules
from pybrain.core.harmonizer import DataHarmonizer, FHIRMapper
from pybrain.core.knowledge import KnowledgeGraph, MedicalOntology

__all__ = [
    "AIEngine",
    "ModelRegistry",
    "AnalyticsEngine",
    "HealthMetrics",
    "DecisionEngine",
    "ClinicalRules",
    "DataHarmonizer",
    "FHIRMapper",
    "KnowledgeGraph",
    "MedicalOntology",
]

# Configure logging
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())