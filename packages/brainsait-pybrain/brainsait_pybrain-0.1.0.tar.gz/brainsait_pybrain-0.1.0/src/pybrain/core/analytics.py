"""
Analytics Engine for population health and predictive analytics
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class HealthMetrics(BaseModel):
    """Health metrics data model"""
    
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    patient_id: Optional[str] = None
    population_segment: Optional[str] = None


class AnalyticsEngine:
    """
    Healthcare analytics engine for population health insights
    """
    
    def __init__(self):
        self.metrics_cache: Dict[str, List[HealthMetrics]] = {}
        self.population_stats: Dict[str, Any] = {}
    
    def analyze_patient_trends(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze individual patient trends
        
        Args:
            patient_data: Patient data including observations
            
        Returns:
            Analysis results with trends and insights
        """
        insights = {
            "patient_id": patient_data.get("patient", {}).get("id"),
            "risk_level": "low",
            "conditions": [],
            "trends": {},
            "recommendations": []
        }
        
        observations = patient_data.get("observations", [])
        
        # Analyze vital signs trends
        vital_trends = self._analyze_vital_trends(observations)
        insights["trends"]["vitals"] = vital_trends
        
        # Determine risk level based on observations
        risk_score = self._calculate_patient_risk(observations)
        if risk_score > 0.8:
            insights["risk_level"] = "high"
        elif risk_score > 0.5:
            insights["risk_level"] = "moderate"
        
        # Extract conditions from patient data
        if "conditions" in patient_data.get("patient", {}):
            insights["conditions"] = patient_data["patient"]["conditions"]
        
        # Generate recommendations
        insights["recommendations"] = self._generate_patient_recommendations(insights)
        
        return insights
    
    def _analyze_vital_trends(self, observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in vital signs"""
        trends = {
            "blood_pressure": {"trend": "stable", "latest": None},
            "heart_rate": {"trend": "stable", "latest": None},
            "temperature": {"trend": "stable", "latest": None},
            "weight": {"trend": "stable", "latest": None}
        }
        
        # Group observations by type
        vital_groups = {}
        for obs in observations:
            code = obs.get("code", {})
            display = code.get("display", "").lower() if code else ""
            
            if "blood pressure" in display:
                vital_groups.setdefault("blood_pressure", []).append(obs)
            elif "heart rate" in display:
                vital_groups.setdefault("heart_rate", []).append(obs)
            elif "temperature" in display:
                vital_groups.setdefault("temperature", []).append(obs)
            elif "weight" in display:
                vital_groups.setdefault("weight", []).append(obs)
        
        # Analyze trends for each vital type
        for vital_type, obs_list in vital_groups.items():
            if len(obs_list) >= 2:
                # Sort by date
                sorted_obs = sorted(obs_list, key=lambda x: x.get("effectiveDateTime", ""))
                
                # Get values
                values = []
                for obs in sorted_obs:
                    value_qty = obs.get("valueQuantity", {})
                    if value_qty.get("value"):
                        values.append(float(value_qty["value"]))
                
                if len(values) >= 2:
                    # Simple trend analysis
                    if values[-1] > values[0] * 1.1:
                        trends[vital_type]["trend"] = "increasing"
                    elif values[-1] < values[0] * 0.9:
                        trends[vital_type]["trend"] = "decreasing"
                    
                    trends[vital_type]["latest"] = values[-1]
        
        return trends
    
    def _calculate_patient_risk(self, observations: List[Dict[str, Any]]) -> float:
        """Calculate overall patient risk based on observations"""
        risk_score = 0.0
        
        for obs in observations:
            value_qty = obs.get("valueQuantity", {})
            if not value_qty.get("value"):
                continue
            
            value = float(value_qty["value"])
            code = obs.get("code", {})
            display = code.get("display", "").lower() if code else ""
            
            # Risk factors based on vital signs
            if "blood pressure" in display and "systolic" in display:
                if value > 140:
                    risk_score += 0.2
                elif value > 130:
                    risk_score += 0.1
            elif "heart rate" in display:
                if value > 100 or value < 60:
                    risk_score += 0.15
            elif "temperature" in display:
                if value > 38 or value < 36:
                    risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _generate_patient_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on patient insights"""
        recommendations = []
        
        risk_level = insights.get("risk_level", "low")
        trends = insights.get("trends", {})
        
        if risk_level == "high":
            recommendations.append("Schedule immediate follow-up appointment")
            recommendations.append("Consider medication adjustment")
        elif risk_level == "moderate":
            recommendations.append("Monitor closely over next 2 weeks")
            recommendations.append("Review lifestyle factors")
        
        # Trend-based recommendations
        vital_trends = trends.get("vitals", {})
        if vital_trends.get("blood_pressure", {}).get("trend") == "increasing":
            recommendations.append("Monitor blood pressure daily")
        if vital_trends.get("weight", {}).get("trend") == "increasing":
            recommendations.append("Review diet and exercise plan")
        
        return recommendations
    
    def calculate_population_metrics(self, population_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate population-level health metrics
        
        Args:
            population_data: List of patient data
            
        Returns:
            Population health metrics and insights
        """
        metrics = {
            "total_patients": len(population_data),
            "risk_distribution": {"high": 0, "moderate": 0, "low": 0},
            "common_conditions": {},
            "average_age": 0,
            "gender_distribution": {"male": 0, "female": 0, "other": 0},
            "recommendations": []
        }
        
        total_age = 0
        age_count = 0
        
        for patient_data in population_data:
            patient = patient_data.get("patient", {})
            
            # Age calculation
            birth_date = patient.get("birthDate")
            if birth_date:
                try:
                    birth_year = int(birth_date.split("-")[0])
                    age = datetime.now().year - birth_year
                    total_age += age
                    age_count += 1
                except:
                    pass
            
            # Gender distribution
            gender = patient.get("gender", "other")
            if gender in metrics["gender_distribution"]:
                metrics["gender_distribution"][gender] += 1
            else:
                metrics["gender_distribution"]["other"] += 1
            
            # Risk assessment
            observations = patient_data.get("observations", [])
            risk_score = self._calculate_patient_risk(observations)
            
            if risk_score > 0.7:
                metrics["risk_distribution"]["high"] += 1
            elif risk_score > 0.4:
                metrics["risk_distribution"]["moderate"] += 1
            else:
                metrics["risk_distribution"]["low"] += 1
            
            # Common conditions
            conditions = patient.get("conditions", [])
            for condition in conditions:
                condition_name = condition.get("display", str(condition))
                metrics["common_conditions"][condition_name] = \
                    metrics["common_conditions"].get(condition_name, 0) + 1
        
        # Calculate averages
        if age_count > 0:
            metrics["average_age"] = total_age / age_count
        
        # Generate population recommendations
        metrics["recommendations"] = self._generate_population_recommendations(metrics)
        
        return metrics
    
    def _generate_population_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate population-level recommendations"""
        recommendations = []
        
        # High-risk population recommendations
        high_risk_pct = metrics["risk_distribution"]["high"] / metrics["total_patients"] * 100
        if high_risk_pct > 20:
            recommendations.append("Implement targeted high-risk patient outreach program")
        
        # Age-specific recommendations
        avg_age = metrics.get("average_age", 0)
        if avg_age > 65:
            recommendations.append("Focus on geriatric care protocols")
            recommendations.append("Increase fall prevention measures")
        
        # Common condition recommendations
        common_conditions = metrics.get("common_conditions", {})
        if common_conditions:
            most_common = max(common_conditions.items(), key=lambda x: x[1])
            recommendations.append(f"Develop care pathway for {most_common[0]}")
        
        return recommendations
    
    def forecast_resource_needs(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forecast healthcare resource needs based on trends
        
        Args:
            historical_data: Historical utilization data
            
        Returns:
            Resource forecasting recommendations
        """
        forecast = {
            "timeframe": "next_30_days",
            "bed_utilization": {},
            "staffing_needs": {},
            "equipment_needs": [],
            "confidence": 0.75
        }
        
        # Simple forecasting based on historical patterns
        # In production, would use more sophisticated ML models
        
        current_utilization = historical_data.get("current_utilization", {})
        
        # Bed utilization forecast
        current_beds = current_utilization.get("beds", 0)
        forecast["bed_utilization"]["predicted"] = current_beds * 1.1  # 10% increase
        
        # Staffing needs
        current_staff = current_utilization.get("staff", 0)
        forecast["staffing_needs"]["nurses"] = current_staff * 1.05  # 5% increase
        
        # Equipment needs based on utilization
        if current_utilization.get("icu_beds", 0) > 0.9:  # 90% utilization
            forecast["equipment_needs"].append("Additional ventilators")
            forecast["equipment_needs"].append("ICU monitoring equipment")
        
        return forecast