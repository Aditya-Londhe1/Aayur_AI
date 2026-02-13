# backend/app/services/report_service.py
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from app.i18n import t

logger = logging.getLogger(__name__)

class ReportService:
    """
    Service for generating consultation reports and health summaries.
    """
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        logger.info("ReportService initialized")
    
    async def generate_consultation_report(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive consultation report
        
        Args:
            consultation: Complete consultation data
            
        Returns:
            Report data with summary and recommendations
        """
        try:
            consultation_id = consultation["consultation_id"]
            locale = consultation.get("locale", "en")
            
            # Generate report sections
            report = {
                "report_id": f"RPT-{consultation_id}",
                "consultation_id": consultation_id,
                "generated_at": datetime.now().isoformat(),
                "locale": locale,
                "patient_summary": self._generate_patient_summary(consultation),
                "analysis_summary": self._generate_analysis_summary(consultation),
                "diagnosis_summary": self._generate_diagnosis_summary(consultation),
                "recommendations": self._format_recommendations(consultation),
                "health_score": self._calculate_health_score(consultation),
                "risk_assessment": self._generate_risk_assessment(consultation),
                "follow_up": self._generate_follow_up_plan(consultation),
                "disclaimer": t("report.disclaimer", locale=locale)
            }
            
            # Save report to file
            report_path = await self._save_report(report)
            report["report_path"] = str(report_path)
            
            logger.info(f"Generated report {report['report_id']}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate consultation report: {e}")
            raise
    
    def _generate_patient_summary(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate patient summary section"""
        patient_info = consultation.get("patient_info", {})
        
        return {
            "age": patient_info.get("age", "Not specified"),
            "gender": patient_info.get("gender", "Not specified"),
            "consultation_date": consultation.get("created_at", ""),
            "consultation_type": "Digital Ayurvedic Assessment",
            "analyses_performed": list(consultation.get("analyses", {}).keys())
        }
    
    def _generate_analysis_summary(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary section"""
        analyses = consultation.get("analyses", {})
        summary = {}
        
        # Tongue analysis summary
        if "tongue" in analyses:
            tongue = analyses["tongue"]
            summary["tongue"] = {
                "dominant_features": tongue.get("dominant_features", []),
                "dosha_indication": tongue.get("dosha_scores", {}),
                "key_findings": tongue.get("key_findings", [])
            }
        
        # Pulse analysis summary
        if "pulse" in analyses:
            pulse = analyses["pulse"]
            summary["pulse"] = {
                "pulse_type": pulse.get("pulse_type", ""),
                "rhythm": pulse.get("rhythm", ""),
                "dosha_indication": pulse.get("dosha_scores", {}),
                "characteristics": pulse.get("characteristics", [])
            }
        
        # Symptom analysis summary
        if "symptoms" in analyses:
            symptoms = analyses["symptoms"]
            summary["symptoms"] = {
                "dominant_dosha": symptoms.get("dominant_dosha", ""),
                "confidence": symptoms.get("confidence", 0.0),
                "likely_conditions": symptoms.get("likely_conditions", []),
                "overall_severity": symptoms.get("overall_severity", "")
            }
        
        return summary
    
    def _generate_diagnosis_summary(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate diagnosis summary section"""
        diagnosis = consultation.get("final_diagnosis", {})
        
        if not diagnosis:
            return {"status": "No diagnosis available"}
        
        return {
            "primary_dosha": diagnosis.get("dominant_dosha", ""),
            "imbalance_level": diagnosis.get("imbalance_level", ""),
            "constitution_type": diagnosis.get("prakriti_type", ""),
            "current_state": diagnosis.get("vikriti_type", ""),
            "dosha_percentages": diagnosis.get("dosha_scores", {}),
            "explanation": diagnosis.get("explanation", ""),
            "confidence_score": consultation.get("confidence_score", 0.0)
        }
    
    def _format_recommendations(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Format recommendations for report"""
        recommendations = consultation.get("recommendations", {})
        
        if not recommendations:
            return {"status": "No recommendations available"}
        
        formatted = {}
        
        # Dietary recommendations
        if "dietary" in recommendations:
            formatted["dietary"] = {
                "title": "Dietary Guidelines",
                "recommendations": recommendations["dietary"][:8],  # Top 8
                "priority": "high"
            }
        
        # Lifestyle recommendations
        if "lifestyle" in recommendations:
            formatted["lifestyle"] = {
                "title": "Lifestyle Modifications",
                "recommendations": recommendations["lifestyle"][:8],
                "priority": "high"
            }
        
        # Herbal recommendations
        if "herbal" in recommendations:
            formatted["herbal"] = {
                "title": "Herbal Support",
                "recommendations": recommendations["herbal"][:6],
                "priority": "medium"
            }
        
        # Yoga and exercise
        if "yoga" in recommendations:
            formatted["yoga"] = {
                "title": "Yoga and Exercise",
                "recommendations": recommendations["yoga"][:6],
                "priority": "medium"
            }
        
        # Precautions
        if "precautions" in recommendations:
            formatted["precautions"] = {
                "title": "Important Precautions",
                "recommendations": recommendations["precautions"],
                "priority": "critical"
            }
        
        return formatted
    
    def _calculate_health_score(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall health score"""
        try:
            diagnosis = consultation.get("final_diagnosis", {})
            confidence = consultation.get("confidence_score", 0.5)
            
            # Base score calculation
            imbalance_level = diagnosis.get("imbalance_level", "mild")
            
            # Score based on imbalance level
            base_scores = {
                "mild": 75,
                "moderate": 60,
                "severe": 40
            }
            
            base_score = base_scores.get(imbalance_level, 70)
            
            # Adjust based on confidence
            adjusted_score = base_score * confidence
            
            # Determine health category
            if adjusted_score >= 80:
                category = "Excellent"
                color = "green"
            elif adjusted_score >= 65:
                category = "Good"
                color = "lightgreen"
            elif adjusted_score >= 50:
                category = "Fair"
                color = "yellow"
            else:
                category = "Needs Attention"
                color = "orange"
            
            return {
                "score": round(adjusted_score, 1),
                "category": category,
                "color": color,
                "factors": {
                    "dosha_balance": imbalance_level,
                    "analysis_confidence": confidence,
                    "symptoms_severity": self._get_symptom_severity(consultation)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return {
                "score": 50.0,
                "category": "Unknown",
                "color": "gray",
                "error": str(e)
            }
    
    def _get_symptom_severity(self, consultation: Dict[str, Any]) -> str:
        """Get overall symptom severity"""
        analyses = consultation.get("analyses", {})
        if "symptoms" in analyses:
            return analyses["symptoms"].get("overall_severity", "mild")
        return "none"
    
    def _generate_risk_assessment(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate health risk assessment"""
        diagnosis = consultation.get("final_diagnosis", {})
        analyses = consultation.get("analyses", {})
        
        risks = []
        
        # Risk based on dominant dosha imbalance
        dominant_dosha = diagnosis.get("dominant_dosha", "")
        imbalance_level = diagnosis.get("imbalance_level", "mild")
        
        if dominant_dosha and imbalance_level != "mild":
            risk_conditions = {
                "vata": ["Anxiety disorders", "Digestive issues", "Joint problems"],
                "pitta": ["Inflammatory conditions", "Skin issues", "Digestive disorders"],
                "kapha": ["Weight gain", "Respiratory issues", "Metabolic disorders"]
            }
            
            for condition in risk_conditions.get(dominant_dosha, []):
                risk_level = "moderate" if imbalance_level == "moderate" else "high"
                risks.append({
                    "condition": condition,
                    "risk_level": risk_level,
                    "related_dosha": dominant_dosha
                })
        
        # Risk based on symptoms
        if "symptoms" in analyses:
            likely_conditions = analyses["symptoms"].get("likely_conditions", [])
            for condition in likely_conditions[:3]:  # Top 3
                risks.append({
                    "condition": condition.get("name", ""),
                    "risk_level": "low" if condition.get("confidence", 0) < 0.5 else "moderate",
                    "confidence": condition.get("confidence", 0)
                })
        
        return {
            "identified_risks": risks[:5],  # Top 5 risks
            "overall_risk_level": self._calculate_overall_risk(risks),
            "prevention_focus": f"Focus on balancing {dominant_dosha} dosha"
        }
    
    def _calculate_overall_risk(self, risks: List[Dict]) -> str:
        """Calculate overall risk level"""
        if not risks:
            return "low"
        
        high_risks = sum(1 for r in risks if r.get("risk_level") == "high")
        moderate_risks = sum(1 for r in risks if r.get("risk_level") == "moderate")
        
        if high_risks > 0:
            return "high"
        elif moderate_risks > 1:
            return "moderate"
        else:
            return "low"
    
    def _generate_follow_up_plan(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate follow-up plan"""
        diagnosis = consultation.get("final_diagnosis", {})
        imbalance_level = diagnosis.get("imbalance_level", "mild")
        
        # Follow-up timeline based on imbalance level
        timelines = {
            "mild": {"weeks": 4, "description": "Monthly check-in recommended"},
            "moderate": {"weeks": 2, "description": "Bi-weekly monitoring suggested"},
            "severe": {"weeks": 1, "description": "Weekly follow-up strongly recommended"}
        }
        
        timeline = timelines.get(imbalance_level, timelines["mild"])
        
        return {
            "next_consultation": f"In {timeline['weeks']} weeks",
            "description": timeline["description"],
            "monitoring_points": [
                "Track symptom changes",
                "Monitor dietary compliance",
                "Assess lifestyle modifications",
                "Evaluate herbal interventions"
            ],
            "red_flags": [
                "Worsening of existing symptoms",
                "New severe symptoms",
                "No improvement after 4 weeks"
            ]
        }
    
    async def _save_report(self, report: Dict[str, Any]) -> Path:
        """Save report to file"""
        try:
            report_id = report["report_id"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_id}_{timestamp}.json"
            
            report_path = self.reports_dir / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Report saved to {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise
    
    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a saved report"""
        try:
            # Find report file
            for report_file in self.reports_dir.glob(f"{report_id}_*.json"):
                with open(report_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve report {report_id}: {e}")
            return None
    
    async def list_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent reports"""
        try:
            reports = []
            
            for report_file in sorted(self.reports_dir.glob("RPT-*.json"), 
                                    key=os.path.getmtime, reverse=True)[:limit]:
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                        
                    reports.append({
                        "report_id": report_data.get("report_id"),
                        "consultation_id": report_data.get("consultation_id"),
                        "generated_at": report_data.get("generated_at"),
                        "patient_age": report_data.get("patient_summary", {}).get("age"),
                        "health_score": report_data.get("health_score", {}).get("score"),
                        "file_path": str(report_file)
                    })
                except Exception as e:
                    logger.warning(f"Failed to read report file {report_file}: {e}")
                    continue
            
            return reports
            
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return []

# Global instance
report_service = ReportService()