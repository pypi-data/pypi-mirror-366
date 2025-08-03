"""
Decision Engine for clinical decision support
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ClinicalRule(BaseModel):
    """Clinical decision rule"""
    
    id: str
    name: str
    condition: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int = 1
    active: bool = True


class ClinicalRules:
    """Collection of clinical decision rules"""
    
    def __init__(self):
        self.rules: List[ClinicalRule] = []
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default clinical decision rules"""
        # High blood pressure alert
        self.rules.append(ClinicalRule(
            id="hypertension_alert",
            name="Hypertension Alert",
            condition={
                "type": "vital_sign",
                "parameter": "systolic_bp",
                "operator": "greater_than",
                "value": 140
            },
            actions=[
                {
                    "type": "alert",
                    "message": "Elevated blood pressure detected",
                    "severity": "medium"
                },
                {
                    "type": "recommendation",
                    "text": "Consider antihypertensive medication review"
                }
            ],
            priority=2
        ))
        
        # Critical temperature alert
        self.rules.append(ClinicalRule(
            id="fever_alert",
            name="High Fever Alert",
            condition={
                "type": "vital_sign",
                "parameter": "temperature",
                "operator": "greater_than",
                "value": 39.0
            },
            actions=[
                {
                    "type": "alert",
                    "message": "High fever detected - immediate attention required",
                    "severity": "high"
                },
                {
                    "type": "order",
                    "item": "Blood cultures",
                    "urgency": "stat"
                }
            ],
            priority=1
        ))
        
        # Drug interaction warning
        self.rules.append(ClinicalRule(
            id="drug_interaction",
            name="Drug Interaction Check",
            condition={
                "type": "medication_combination",
                "drugs": ["warfarin", "aspirin"],
                "operator": "both_present"
            },
            actions=[
                {
                    "type": "warning",
                    "message": "Potential bleeding risk with warfarin + aspirin combination",
                    "severity": "high"
                },
                {
                    "type": "recommendation",
                    "text": "Monitor INR closely and consider PPI prophylaxis"
                }
            ],
            priority=1
        ))
    
    def add_rule(self, rule: ClinicalRule):
        """Add a new clinical rule"""
        self.rules.append(rule)
        logger.info(f"Added clinical rule: {rule.name}")
    
    def get_active_rules(self) -> List[ClinicalRule]:
        """Get all active clinical rules"""
        return [rule for rule in self.rules if rule.active]


class DecisionEngine:
    """
    Clinical decision support engine
    """
    
    def __init__(self):
        self.clinical_rules = ClinicalRules()
        self.decision_cache: Dict[str, Any] = {}
    
    def evaluate_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate patient data against clinical rules
        
        Args:
            patient_data: Complete patient data
            
        Returns:
            Decision support recommendations
        """
        recommendations = {
            "patient_id": patient_data.get("id"),
            "alerts": [],
            "warnings": [],
            "recommendations": [],
            "orders": [],
            "evaluated_at": datetime.utcnow().isoformat()
        }
        
        # Evaluate against all active rules
        for rule in self.clinical_rules.get_active_rules():
            if self._evaluate_rule_condition(rule.condition, patient_data):
                # Rule condition met, execute actions
                for action in rule.actions:
                    self._execute_action(action, recommendations)
        
        # Sort by severity/priority
        recommendations["alerts"] = sorted(
            recommendations["alerts"], 
            key=lambda x: self._get_severity_priority(x.get("severity", "low"))
        )
        
        return recommendations
    
    def _evaluate_rule_condition(self, condition: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate if a rule condition is met"""
        condition_type = condition.get("type")
        
        if condition_type == "vital_sign":
            return self._evaluate_vital_condition(condition, patient_data)
        elif condition_type == "medication_combination":
            return self._evaluate_medication_condition(condition, patient_data)
        elif condition_type == "lab_value":
            return self._evaluate_lab_condition(condition, patient_data)
        elif condition_type == "diagnosis":
            return self._evaluate_diagnosis_condition(condition, patient_data)
        
        return False
    
    def _evaluate_vital_condition(self, condition: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate vital signs condition"""
        parameter = condition.get("parameter")
        operator = condition.get("operator")
        threshold = condition.get("value")
        
        # Get latest vital sign value
        observations = patient_data.get("observations", [])
        for obs in reversed(observations):  # Check most recent first
            code = obs.get("code", {})
            display = code.get("display", "").lower() if code else ""
            
            # Match parameter to observation
            if parameter == "systolic_bp" and "blood pressure" in display and "systolic" in display:
                value_qty = obs.get("valueQuantity", {})
                if value_qty.get("value"):
                    return self._compare_values(float(value_qty["value"]), operator, threshold)
            
            elif parameter == "temperature" and "temperature" in display:
                value_qty = obs.get("valueQuantity", {})
                if value_qty.get("value"):
                    return self._compare_values(float(value_qty["value"]), operator, threshold)
            
            elif parameter == "heart_rate" and "heart rate" in display:
                value_qty = obs.get("valueQuantity", {})
                if value_qty.get("value"):
                    return self._compare_values(float(value_qty["value"]), operator, threshold)
        
        return False
    
    def _evaluate_medication_condition(self, condition: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate medication combination condition"""
        required_drugs = condition.get("drugs", [])
        operator = condition.get("operator")
        
        # Get current medications
        medications = patient_data.get("medications", [])
        current_drugs = []
        
        for med in medications:
            med_concept = med.get("medicationCodeableConcept", {})
            codings = med_concept.get("coding", [])
            for coding in codings:
                display = coding.get("display", "").lower()
                current_drugs.append(display)
        
        if operator == "both_present":
            return all(any(drug.lower() in current_drug for current_drug in current_drugs) 
                      for drug in required_drugs)
        elif operator == "any_present":
            return any(any(drug.lower() in current_drug for current_drug in current_drugs) 
                      for drug in required_drugs)
        
        return False
    
    def _evaluate_lab_condition(self, condition: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate laboratory value condition"""
        parameter = condition.get("parameter")
        operator = condition.get("operator")
        threshold = condition.get("value")
        
        observations = patient_data.get("observations", [])
        for obs in reversed(observations):
            code = obs.get("code", {})
            codings = code.get("coding", []) if code else []
            
            # Check if this is the lab value we're looking for
            for coding in codings:
                if parameter.lower() in coding.get("display", "").lower():
                    value_qty = obs.get("valueQuantity", {})
                    if value_qty.get("value"):
                        return self._compare_values(float(value_qty["value"]), operator, threshold)
        
        return False
    
    def _evaluate_diagnosis_condition(self, condition: Dict[str, Any], patient_data: Dict[str, Any]) -> bool:
        """Evaluate diagnosis condition"""
        required_diagnosis = condition.get("diagnosis", "").lower()
        
        conditions = patient_data.get("conditions", [])
        for cond in conditions:
            if isinstance(cond, dict):
                display = cond.get("display", "").lower()
            else:
                display = str(cond).lower()
            
            if required_diagnosis in display:
                return True
        
        return False
    
    def _compare_values(self, value: float, operator: str, threshold: float) -> bool:
        """Compare values based on operator"""
        if operator == "greater_than":
            return value > threshold
        elif operator == "less_than":
            return value < threshold
        elif operator == "equal_to":
            return abs(value - threshold) < 0.01
        elif operator == "greater_equal":
            return value >= threshold
        elif operator == "less_equal":
            return value <= threshold
        
        return False
    
    def _execute_action(self, action: Dict[str, Any], recommendations: Dict[str, Any]):
        """Execute a rule action"""
        action_type = action.get("type")
        
        if action_type == "alert":
            recommendations["alerts"].append({
                "message": action.get("message"),
                "severity": action.get("severity", "medium"),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action_type == "warning":
            recommendations["warnings"].append({
                "message": action.get("message"),
                "severity": action.get("severity", "medium"),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action_type == "recommendation":
            recommendations["recommendations"].append({
                "text": action.get("text"),
                "category": action.get("category", "clinical"),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action_type == "order":
            recommendations["orders"].append({
                "item": action.get("item"),
                "urgency": action.get("urgency", "routine"),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def _get_severity_priority(self, severity: str) -> int:
        """Get numeric priority for severity level"""
        priorities = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }
        return priorities.get(severity, 5)
    
    def generate_population_interventions(self, population_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate population-level intervention recommendations
        
        Args:
            population_data: Population health statistics
            
        Returns:
            List of intervention recommendations
        """
        interventions = []
        
        # High-risk population intervention
        risk_dist = population_data.get("risk_stratification", {})
        high_risk_count = risk_dist.get("high", 0)
        total_patients = population_data.get("total_patients", 1)
        
        if high_risk_count / total_patients > 0.15:  # >15% high risk
            interventions.append({
                "type": "care_management",
                "priority": "high",
                "target": "high_risk_patients",
                "description": "Implement intensive care management program",
                "expected_impact": "30% reduction in readmissions",
                "resources_required": "Care coordinators, remote monitoring"
            })
        
        # Disease-specific interventions
        disease_prevalence = population_data.get("disease_prevalence", {})
        for disease, count in disease_prevalence.items():
            prevalence_rate = count / total_patients
            if prevalence_rate > 0.2:  # >20% prevalence
                interventions.append({
                    "type": "disease_management",
                    "priority": "medium",
                    "target": f"{disease}_patients",
                    "description": f"Develop specialized {disease} care pathway",
                    "expected_impact": "Improved outcomes and reduced costs",
                    "resources_required": "Specialist consultation, patient education"
                })
        
        # Resource utilization interventions
        if population_data.get("average_los", 0) > 5:  # Average length of stay > 5 days
            interventions.append({
                "type": "discharge_planning",
                "priority": "medium",
                "target": "all_patients",
                "description": "Enhanced discharge planning program",
                "expected_impact": "Reduced length of stay by 1-2 days",
                "resources_required": "Discharge planners, community liaisons"
            })
        
        return interventions
    
    def assess_clinical_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive clinical risk assessment
        
        Args:
            patient_data: Patient clinical data
            
        Returns:
            Risk assessment with scores and factors
        """
        risk_assessment = {
            "overall_risk": "low",
            "risk_score": 0.0,
            "risk_factors": [],
            "protective_factors": [],
            "recommendations": []
        }
        
        risk_score = 0.0
        
        # Age-based risk
        age = self._calculate_age(patient_data.get("birthDate"))
        if age:
            if age > 75:
                risk_score += 0.3
                risk_assessment["risk_factors"].append("Advanced age (>75)")
            elif age > 65:
                risk_score += 0.2
                risk_assessment["risk_factors"].append("Elderly (65-75)")
            elif age < 40:
                risk_assessment["protective_factors"].append("Younger age")
        
        # Comorbidity risk
        conditions = patient_data.get("conditions", [])
        high_risk_conditions = ["heart failure", "diabetes", "copd", "cancer", "kidney disease"]
        
        for condition in conditions:
            condition_str = str(condition).lower()
            for hr_condition in high_risk_conditions:
                if hr_condition in condition_str:
                    risk_score += 0.2
                    risk_assessment["risk_factors"].append(f"Diagnosis: {hr_condition}")
        
        # Medication complexity
        medications = patient_data.get("medications", [])
        if len(medications) > 10:
            risk_score += 0.2
            risk_assessment["risk_factors"].append("Polypharmacy (>10 medications)")
        elif len(medications) > 5:
            risk_score += 0.1
            risk_assessment["risk_factors"].append("Multiple medications (5-10)")
        
        # Recent hospitalizations
        encounters = patient_data.get("encounters", [])
        recent_admissions = [enc for enc in encounters 
                           if enc.get("class", {}).get("code") == "IMP"]  # Inpatient
        
        if len(recent_admissions) > 2:
            risk_score += 0.3
            risk_assessment["risk_factors"].append("Multiple recent hospitalizations")
        elif len(recent_admissions) > 0:
            risk_score += 0.1
            risk_assessment["risk_factors"].append("Recent hospitalization")
        
        # Determine overall risk level
        risk_assessment["risk_score"] = min(risk_score, 1.0)
        
        if risk_score > 0.7:
            risk_assessment["overall_risk"] = "high"
        elif risk_score > 0.4:
            risk_assessment["overall_risk"] = "moderate"
        else:
            risk_assessment["overall_risk"] = "low"
        
        # Generate recommendations
        risk_assessment["recommendations"] = self._generate_risk_recommendations(risk_assessment)
        
        return risk_assessment
    
    def _calculate_age(self, birth_date: Optional[str]) -> Optional[int]:
        """Calculate age from birth date"""
        if not birth_date:
            return None
        
        try:
            birth_year = int(birth_date.split("-")[0])
            return datetime.now().year - birth_year
        except:
            return None
    
    def _generate_risk_recommendations(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        overall_risk = risk_assessment.get("overall_risk")
        risk_factors = risk_assessment.get("risk_factors", [])
        
        if overall_risk == "high":
            recommendations.append("Enroll in high-risk care management program")
            recommendations.append("Schedule monthly provider visits")
            recommendations.append("Consider remote monitoring")
        elif overall_risk == "moderate":
            recommendations.append("Increase monitoring frequency")
            recommendations.append("Review medication management")
        
        # Specific recommendations based on risk factors
        if any("age" in factor.lower() for factor in risk_factors):
            recommendations.append("Implement fall prevention measures")
            recommendations.append("Annual comprehensive geriatric assessment")
        
        if any("polypharmacy" in factor.lower() for factor in risk_factors):
            recommendations.append("Pharmacy consultation for medication review")
            recommendations.append("Consider deprescribing opportunities")
        
        if any("hospitalization" in factor.lower() for factor in risk_factors):
            recommendations.append("Enhanced discharge planning")
            recommendations.append("30-day post-discharge follow-up")
        
        return recommendations