"""Tests for AI engine."""

import pytest
from pybrain.core.ai import AIEngine, ModelConfig


def test_ai_engine_initialization():
    """Test AI engine initialization."""
    engine = AIEngine()
    assert engine.config.model_name == "clinical-bert"
    assert engine.config.model_type == "nlp"


def test_clinical_entity_extraction():
    """Test clinical entity extraction."""
    engine = AIEngine()
    text = "Patient has diabetes and is taking metformin"
    entities = engine.extract_clinical_entities(text)
    
    assert "conditions" in entities
    assert "medications" in entities
    assert "diabetes" in str(entities["conditions"]).lower()
    assert "metformin" in str(entities["medications"]).lower()


def test_risk_score_prediction():
    """Test risk score prediction."""
    engine = AIEngine()
    patient_data = {
        "age": 70,
        "conditions": ["diabetes", "hypertension"],
        "bmi": 30
    }
    
    risk_score = engine.predict_risk_score(patient_data)
    assert 0 <= risk_score <= 1
    assert risk_score > 0.3  # Should be elevated due to age and conditions


def test_model_config():
    """Test model configuration."""
    config = ModelConfig(
        model_name="test-model",
        model_type="vision",
        version="2.0.0"
    )
    
    engine = AIEngine(config)
    assert engine.config.model_name == "test-model"
    assert engine.config.model_type == "vision"
    assert engine.config.version == "2.0.0"