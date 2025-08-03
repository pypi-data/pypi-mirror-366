"""
Knowledge Graph and Medical Ontology management
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class MedicalConcept(BaseModel):
    """Medical concept in the knowledge graph"""
    
    id: str
    name: str
    concept_type: str  # condition, medication, procedure, etc.
    synonyms: List[str] = []
    codes: Dict[str, str] = {}  # coding system -> code
    relationships: Dict[str, List[str]] = {}  # relationship type -> related concept IDs


class PatientProfile(BaseModel):
    """Patient profile for similarity matching"""
    
    patient_id: str
    demographics: Dict[str, Any]
    conditions: List[str]
    medications: List[str]
    procedures: List[str]
    outcomes: Dict[str, float]
    last_updated: datetime


class KnowledgeGraph:
    """
    Medical knowledge graph for clinical reasoning
    """
    
    def __init__(self):
        self.concepts: Dict[str, MedicalConcept] = {}
        self.patient_profiles: Dict[str, PatientProfile] = {}
        self.relationship_weights: Dict[str, float] = {}
        self._initialize_base_concepts()
    
    def _initialize_base_concepts(self):
        """Initialize basic medical concepts"""
        # Common conditions
        diabetes_concept = MedicalConcept(
            id="diabetes_mellitus",
            name="Diabetes Mellitus",
            concept_type="condition",
            synonyms=["diabetes", "DM", "diabetes mellitus type 2"],
            codes={
                "ICD-10": "E11",
                "SNOMED": "44054006"
            },
            relationships={
                "causes": ["diabetic_nephropathy", "diabetic_retinopathy"],
                "risk_factors": ["obesity", "family_history"],
                "treatments": ["metformin", "insulin"]
            }
        )
        self.concepts[diabetes_concept.id] = diabetes_concept
        
        # Hypertension
        htn_concept = MedicalConcept(
            id="hypertension",
            name="Hypertension",
            concept_type="condition",
            synonyms=["high blood pressure", "HTN"],
            codes={
                "ICD-10": "I10",
                "SNOMED": "38341003"
            },
            relationships={
                "causes": ["stroke", "heart_disease", "kidney_disease"],
                "risk_factors": ["age", "obesity", "smoking"],
                "treatments": ["lisinopril", "amlodipine", "losartan"]
            }
        )
        self.concepts[htn_concept.id] = htn_concept
        
        # Common medications
        metformin_concept = MedicalConcept(
            id="metformin",
            name="Metformin",
            concept_type="medication",
            synonyms=["metformin hydrochloride"],
            codes={
                "RxNorm": "6809",
                "ATC": "A10BA02"
            },
            relationships={
                "treats": ["diabetes_mellitus"],
                "contraindications": ["kidney_disease"],
                "side_effects": ["nausea", "diarrhea"]
            }
        )
        self.concepts[metformin_concept.id] = metformin_concept
        
        logger.info(f"Initialized {len(self.concepts)} base medical concepts")
    
    def add_concept(self, concept: MedicalConcept):
        """Add a new medical concept to the knowledge graph"""
        self.concepts[concept.id] = concept
        logger.info(f"Added medical concept: {concept.name}")
    
    def find_concept(self, query: str) -> Optional[MedicalConcept]:
        """Find a medical concept by name or synonym"""
        query_lower = query.lower()
        
        # Search by exact name match
        for concept in self.concepts.values():
            if concept.name.lower() == query_lower:
                return concept
        
        # Search by synonyms
        for concept in self.concepts.values():
            if any(synonym.lower() == query_lower for synonym in concept.synonyms):
                return concept
        
        # Search by partial match
        for concept in self.concepts.values():
            if query_lower in concept.name.lower():
                return concept
            if any(query_lower in synonym.lower() for synonym in concept.synonyms):
                return concept
        
        return None
    
    def get_related_concepts(self, concept_id: str, relationship_type: str) -> List[MedicalConcept]:
        """Get concepts related to a given concept"""
        concept = self.concepts.get(concept_id)
        if not concept:
            return []
        
        related_ids = concept.relationships.get(relationship_type, [])
        return [self.concepts[rid] for rid in related_ids if rid in self.concepts]
    
    def find_treatment_options(self, condition: str) -> List[Dict[str, Any]]:
        """Find treatment options for a given condition"""
        concept = self.find_concept(condition)
        if not concept:
            return []
        
        treatments = self.get_related_concepts(concept.id, "treatments")
        
        treatment_options = []
        for treatment in treatments:
            treatment_info = {
                "medication": treatment.name,
                "codes": treatment.codes,
                "contraindications": self.get_related_concepts(treatment.id, "contraindications"),
                "side_effects": self.get_related_concepts(treatment.id, "side_effects")
            }
            treatment_options.append(treatment_info)
        
        return treatment_options
    
    def check_drug_interactions(self, medications: List[str]) -> List[Dict[str, Any]]:
        """Check for potential drug interactions"""
        interactions = []
        
        # Find concepts for all medications
        med_concepts = []
        for med in medications:
            concept = self.find_concept(med)
            if concept:
                med_concepts.append(concept)
        
        # Check for interactions between medication pairs
        for i, med1 in enumerate(med_concepts):
            for med2 in med_concepts[i+1:]:
                # Simple interaction detection based on shared contraindications
                med1_contras = self.get_related_concepts(med1.id, "contraindications")
                med2_treats = self.get_related_concepts(med2.id, "treats")
                
                # Check if med2 treats something that med1 is contraindicated for
                for contra in med1_contras:
                    if contra in med2_treats:
                        interactions.append({
                            "medication1": med1.name,
                            "medication2": med2.name,
                            "interaction_type": "contraindication",
                            "severity": "high",
                            "description": f"{med1.name} contraindicated with {contra.name}"
                        })
        
        return interactions
    
    def add_clinical_finding(self, patient_id: str, finding: Dict[str, Any]):
        """Add a clinical finding to patient profile"""
        if patient_id not in self.patient_profiles:
            self.patient_profiles[patient_id] = PatientProfile(
                patient_id=patient_id,
                demographics={},
                conditions=[],
                medications=[],
                procedures=[],
                outcomes={},
                last_updated=datetime.utcnow()
            )
        
        profile = self.patient_profiles[patient_id]
        
        # Update profile based on finding type
        finding_type = finding.get("type", "")
        
        if finding_type == "condition":
            condition = finding.get("condition", "")
            if condition and condition not in profile.conditions:
                profile.conditions.append(condition)
        
        elif finding_type == "medication":
            medication = finding.get("medication", "")
            if medication and medication not in profile.medications:
                profile.medications.append(medication)
        
        elif finding_type == "outcome":
            outcome_type = finding.get("outcome_type", "")
            outcome_value = finding.get("value", 0.0)
            if outcome_type:
                profile.outcomes[outcome_type] = outcome_value
        
        profile.last_updated = datetime.utcnow()
        logger.info(f"Added clinical finding for patient {patient_id}")
    
    def find_similar_patients(self, patient_features: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar patients based on clinical features"""
        target_conditions = set(patient_features.get("conditions", []))
        target_medications = set(patient_features.get("medications", []))
        target_age = patient_features.get("demographics", {}).get("age", 0)
        
        similarities = []
        
        for patient_id, profile in self.patient_profiles.items():
            similarity_score = self._calculate_patient_similarity(
                target_conditions, target_medications, target_age, profile
            )
            
            if similarity_score > 0.3:  # Minimum similarity threshold
                similarities.append({
                    "patient_id": patient_id,
                    "similarity_score": similarity_score,
                    "outcomes": profile.outcomes,
                    "conditions": profile.conditions,
                    "medications": profile.medications
                })
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similarities[:top_k]
    
    def _calculate_patient_similarity(self, 
                                    target_conditions: set, 
                                    target_medications: set,
                                    target_age: int,
                                    profile: PatientProfile) -> float:
        """Calculate similarity between target patient and profile"""
        profile_conditions = set(profile.conditions)
        profile_medications = set(profile.medications)
        profile_age = profile.demographics.get("age", 0)
        
        # Condition similarity (Jaccard index)
        condition_similarity = 0.0
        if target_conditions or profile_conditions:
            intersection = len(target_conditions.intersection(profile_conditions))
            union = len(target_conditions.union(profile_conditions))
            condition_similarity = intersection / union if union > 0 else 0.0
        
        # Medication similarity
        medication_similarity = 0.0
        if target_medications or profile_medications:
            intersection = len(target_medications.intersection(profile_medications))
            union = len(target_medications.union(profile_medications))
            medication_similarity = intersection / union if union > 0 else 0.0
        
        # Age similarity (normalized difference)
        age_similarity = 1.0
        if target_age > 0 and profile_age > 0:
            age_diff = abs(target_age - profile_age)
            age_similarity = max(0.0, 1.0 - age_diff / 50.0)  # Normalize by 50 years
        
        # Weighted combination
        overall_similarity = (
            condition_similarity * 0.5 +
            medication_similarity * 0.3 +
            age_similarity * 0.2
        )
        
        return overall_similarity
    
    def get_clinical_pathways(self, condition: str) -> Dict[str, Any]:
        """Get clinical pathways for a condition"""
        concept = self.find_concept(condition)
        if not concept:
            return {}
        
        pathway = {
            "condition": concept.name,
            "treatments": [],
            "monitoring": [],
            "complications": [],
            "prevention": []
        }
        
        # Get treatment options
        treatments = self.get_related_concepts(concept.id, "treatments")
        pathway["treatments"] = [t.name for t in treatments]
        
        # Get potential complications
        complications = self.get_related_concepts(concept.id, "causes")
        pathway["complications"] = [c.name for c in complications]
        
        # Get risk factors (for prevention)
        risk_factors = self.get_related_concepts(concept.id, "risk_factors")
        pathway["prevention"] = [f"Address {rf.name}" for rf in risk_factors]
        
        return pathway


class MedicalOntology:
    """
    Medical ontology management for standardized terminology
    """
    
    def __init__(self):
        self.terminology_maps: Dict[str, Dict[str, str]] = {}
        self.hierarchy: Dict[str, List[str]] = {}
        self._load_basic_mappings()
    
    def _load_basic_mappings(self):
        """Load basic terminology mappings"""
        # ICD-10 to SNOMED mappings (simplified)
        self.terminology_maps["icd10_to_snomed"] = {
            "E11": "44054006",  # Type 2 diabetes
            "I10": "38341003",  # Hypertension
            "J44": "13645005",  # COPD
            "N18": "709044004", # Chronic kidney disease
        }
        
        # LOINC to common names
        self.terminology_maps["loinc_to_name"] = {
            "2345-7": "Glucose",
            "2160-0": "Creatinine",
            "33747-0": "Hemoglobin A1c",
            "2571-8": "Triglycerides"
        }
        
        # Drug class hierarchy
        self.hierarchy["antidiabetic"] = [
            "metformin", "insulin", "sulfonylureas", "sglt2_inhibitors"
        ]
        self.hierarchy["antihypertensive"] = [
            "ace_inhibitors", "arbs", "beta_blockers", "calcium_channel_blockers"
        ]
    
    def map_code(self, source_system: str, target_system: str, code: str) -> Optional[str]:
        """Map a code from one terminology system to another"""
        mapping_key = f"{source_system}_to_{target_system}"
        mapping = self.terminology_maps.get(mapping_key, {})
        return mapping.get(code)
    
    def get_parent_concepts(self, concept: str) -> List[str]:
        """Get parent concepts in the hierarchy"""
        parents = []
        for parent, children in self.hierarchy.items():
            if concept in children:
                parents.append(parent)
        return parents
    
    def get_child_concepts(self, concept: str) -> List[str]:
        """Get child concepts in the hierarchy"""
        return self.hierarchy.get(concept, [])
    
    def is_related(self, concept1: str, concept2: str) -> bool:
        """Check if two concepts are related in the hierarchy"""
        # Check if one is parent of the other
        if concept2 in self.get_child_concepts(concept1):
            return True
        if concept1 in self.get_child_concepts(concept2):
            return True
        
        # Check if they share a parent
        parents1 = self.get_parent_concepts(concept1)
        parents2 = self.get_parent_concepts(concept2)
        return bool(set(parents1).intersection(set(parents2)))
    
    def add_mapping(self, source_system: str, target_system: str, mappings: Dict[str, str]):
        """Add custom terminology mappings"""
        mapping_key = f"{source_system}_to_{target_system}"
        if mapping_key not in self.terminology_maps:
            self.terminology_maps[mapping_key] = {}
        
        self.terminology_maps[mapping_key].update(mappings)
        logger.info(f"Added {len(mappings)} mappings for {mapping_key}")
    
    def standardize_term(self, term: str, target_system: str = "snomed") -> Optional[str]:
        """Standardize a clinical term to a target terminology"""
        term_lower = term.lower()
        
        # Simple mapping based on common terms
        common_mappings = {
            "diabetes": "44054006",  # SNOMED for diabetes mellitus
            "high blood pressure": "38341003",  # SNOMED for hypertension
            "heart attack": "22298006",  # SNOMED for myocardial infarction
            "stroke": "230690007",  # SNOMED for stroke
        }
        
        return common_mappings.get(term_lower)