"""
PDF Report Generation Service
Creates professional PDF reports for Ayurvedic consultations
"""

import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


class PDFReportService:
    """Service for generating professional PDF reports"""
    
    def __init__(self):
        self.reports_dir = Path("reports/pdf")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to find logo in multiple locations
        self.logo_path = None
        possible_logo_paths = [
            Path("frontend/public/logo.png"),
            Path("../frontend/public/logo.png"),
            Path("static/logo.png"),
            Path("logo.png")
        ]
        
        for path in possible_logo_paths:
            if path.exists():
                self.logo_path = path
                logger.info(f"Logo found at: {path}")
                break
        
        if not self.logo_path:
            logger.warning("Logo file not found, will use text header")
        
        logger.info("PDFReportService initialized")
    
    def generate_pdf_report(self, diagnosis_data: Dict[str, Any], user_info: Dict[str, Any] = None) -> str:
        """
        Generate a professional PDF report
        
        Args:
            diagnosis_data: Complete diagnosis data
            user_info: User information (optional)
            
        Returns:
            Path to generated PDF file
        """
        try:
            logger.info("Starting PDF generation")
            logger.info(f"Diagnosis data keys: {list(diagnosis_data.keys())}")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AayurAI_Report_{timestamp}.pdf"
            filepath = self.reports_dir / filename
            
            logger.info(f"PDF will be saved to: {filepath}")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=0.75*inch
            )
            
            # Build content
            story = []
            styles = self._get_styles()
            
            logger.info("Adding header section")
            # Add header
            story.extend(self._create_header(styles, user_info))
            story.append(Spacer(1, 0.3*inch))
            
            logger.info("Adding executive summary")
            # Add executive summary
            story.extend(self._create_executive_summary(diagnosis_data, styles))
            story.append(Spacer(1, 0.2*inch))
            
            logger.info("Adding dosha analysis")
            # Add dosha analysis
            story.extend(self._create_dosha_analysis(diagnosis_data, styles))
            story.append(Spacer(1, 0.2*inch))
            
            # Add detailed analysis sections
            if diagnosis_data.get('pulse_analysis'):
                logger.info("Adding pulse analysis")
                story.extend(self._create_pulse_section(diagnosis_data['pulse_analysis'], styles))
                story.append(Spacer(1, 0.2*inch))
            
            if diagnosis_data.get('tongue_analysis'):
                logger.info("Adding tongue analysis")
                story.extend(self._create_tongue_section(diagnosis_data['tongue_analysis'], styles))
                story.append(Spacer(1, 0.2*inch))
            
            if diagnosis_data.get('symptom_analysis'):
                logger.info("Adding symptom analysis")
                story.extend(self._create_symptom_section(diagnosis_data['symptom_analysis'], styles))
                story.append(Spacer(1, 0.2*inch))
            
            # Add fusion details
            if diagnosis_data.get('fusion_details'):
                logger.info("Adding fusion analysis")
                story.extend(self._create_fusion_section(diagnosis_data['fusion_details'], styles))
                story.append(Spacer(1, 0.2*inch))
            
            # Add recommendations
            logger.info("Adding recommendations")
            story.extend(self._create_recommendations(diagnosis_data, styles))
            story.append(Spacer(1, 0.2*inch))
            
            # Add home remedies
            if diagnosis_data.get('home_remedies'):
                logger.info("Adding home remedies")
                story.extend(self._create_remedies_section(diagnosis_data['home_remedies'], styles))
                story.append(Spacer(1, 0.2*inch))
            
            # Add disclaimer
            logger.info("Adding disclaimer")
            story.extend(self._create_disclaimer(styles))
            
            # Build PDF
            logger.info("Building PDF document")
            doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            
            logger.info(f"PDF report generated successfully: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}", exc_info=True)
            raise
    
    def _get_styles(self):
        """Get custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0ea5e9'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Subheading style
        styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#475569'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body style
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Highlight style
        styles.add(ParagraphStyle(
            name='Highlight',
            parent=styles['BodyText'],
            fontSize=12,
            textColor=colors.HexColor('#0ea5e9'),
            fontName='Helvetica-Bold'
        ))
        
        return styles
    
    def _create_header(self, styles, user_info):
        """Create report header"""
        elements = []
        
        # Add logo if available
        if self.logo_path and self.logo_path.exists():
            try:
                logo = Image(str(self.logo_path), width=1.5*inch, height=1.5*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.2*inch))
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
        
        # Title
        elements.append(Paragraph("🌿 AayurAI", styles['CustomTitle']))
        elements.append(Paragraph("Ayurvedic Health Assessment Report", styles['CustomHeading']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Report info
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        elements.append(Paragraph(f"<b>Report Generated:</b> {report_date}", styles['CustomBody']))
        
        if user_info:
            if user_info.get('full_name'):
                elements.append(Paragraph(f"<b>Patient Name:</b> {user_info['full_name']}", styles['CustomBody']))
            if user_info.get('email'):
                elements.append(Paragraph(f"<b>Email:</b> {user_info['email']}", styles['CustomBody']))
        
        # Horizontal line
        elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_executive_summary(self, data, styles):
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", styles['CustomHeading']))
        
        # Extract dosha info - handle both formats with defaults
        primary_dosha = data.get('primary_dosha') or data.get('dominant_dosha') or 'Unknown'
        imbalance_level = data.get('imbalance_level') or 'Unknown'
        confidence = data.get('confidence') or 0
        
        # Ensure confidence is a number
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0
        
        summary_text = f"""
        Based on comprehensive AI-powered analysis of pulse, tongue, and symptoms, 
        your primary dosha is <b>{str(primary_dosha).upper()}</b> with <b>{str(imbalance_level)}</b> level of imbalance.
        The AI system has <b>{confidence*100:.1f}% confidence</b> in this assessment.
        This report provides personalized recommendations to restore balance and improve your health.
        """
        
        elements.append(Paragraph(summary_text, styles['CustomBody']))
        
        # Add patient info if available
        if data.get('patient_info'):
            patient = data['patient_info']
            name = patient.get('name', 'N/A')
            age = patient.get('age', 'N/A')
            gender = patient.get('gender', 'N/A')
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"<b>Patient:</b> {name}, Age: {age}, Gender: {gender}", styles['CustomBody']))
        
        return elements
    
    def _create_dosha_analysis(self, data, styles):
        """Create dosha analysis section with table"""
        elements = []
        
        elements.append(Paragraph("Dosha Analysis", styles['CustomHeading']))
        
        # Get dosha scores - handle different formats
        dosha_scores = data.get('dosha_scores', {})
        
        if not dosha_scores:
            elements.append(Paragraph("Dosha scores not available", styles['CustomBody']))
            return elements
        
        # Normalize keys to title case
        normalized_scores = {}
        for key, value in dosha_scores.items():
            if key and value is not None:
                normalized_key = str(key).capitalize() if str(key).lower() in ['vata', 'pitta', 'kapha'] else str(key)
                try:
                    normalized_scores[normalized_key] = float(value)
                except (TypeError, ValueError):
                    normalized_scores[normalized_key] = 0
        
        # Create table data
        table_data = [
            ['Dosha', 'Percentage', 'Status'],
        ]
        
        for dosha in ['Vata', 'Pitta', 'Kapha']:
            score = normalized_scores.get(dosha, 0)
            # Handle both decimal (0.33) and percentage (33) formats
            if score > 1:
                score = score / 100
            score_pct = score * 100
            status = "Balanced" if 30 <= score_pct <= 40 else "Imbalanced"
            table_data.append([dosha, f"{score_pct:.1f}%", status])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        
        # Add explanation if available
        if data.get('explanation'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"<b>Analysis:</b> {data['explanation']}", styles['CustomBody']))
        
        return elements
    
    def _create_pulse_section(self, pulse_data, styles):
        """Create pulse analysis section"""
        elements = []
        
        elements.append(Paragraph("Pulse Analysis (Nadi Pariksha)", styles['CustomHeading']))
        
        if not pulse_data:
            elements.append(Paragraph("Pulse analysis data not available", styles['CustomBody']))
            return elements
        
        # Handle ayurvedic_analysis structure
        ayurvedic = pulse_data.get('ayurvedic_analysis', {})
        
        if ayurvedic:
            # Traditional characteristics
            if ayurvedic.get('traditional_characteristics'):
                chars = ayurvedic['traditional_characteristics']
                elements.append(Paragraph(f"<b>Gati (Movement):</b> {chars.get('gati', 'N/A')}", styles['CustomBody']))
                elements.append(Paragraph(f"<b>Speed:</b> {chars.get('speed', 'N/A')}", styles['CustomBody']))
                elements.append(Paragraph(f"<b>Force:</b> {chars.get('force', 'N/A')}", styles['CustomBody']))
                elements.append(Paragraph(f"<b>Rhythm:</b> {chars.get('rhythm', 'N/A')}", styles['CustomBody']))
            
            # Interpretation
            if ayurvedic.get('interpretation'):
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph("<b>Interpretation:</b>", styles['CustomSubheading']))
                elements.append(Paragraph(str(ayurvedic['interpretation']), styles['CustomBody']))
            
            # Insights
            if ayurvedic.get('ayurvedic_insights'):
                insights = ayurvedic['ayurvedic_insights']
                if isinstance(insights, list) and len(insights) > 0:
                    elements.append(Spacer(1, 0.1*inch))
                    elements.append(Paragraph("<b>Ayurvedic Insights:</b>", styles['CustomSubheading']))
                    for insight in insights[:5]:
                        if insight:
                            elements.append(Paragraph(f"• {str(insight)}", styles['CustomBody']))
            
            # Recommendations
            if ayurvedic.get('recommendations'):
                recs = ayurvedic['recommendations']
                if isinstance(recs, list) and len(recs) > 0:
                    elements.append(Spacer(1, 0.1*inch))
                    elements.append(Paragraph("<b>Pulse-Based Recommendations:</b>", styles['CustomSubheading']))
                    for rec in recs[:5]:
                        if rec:
                            elements.append(Paragraph(f"• {str(rec)}", styles['CustomBody']))
        
        # ML predictions - check both possible keys
        probs = pulse_data.get('probabilities') or pulse_data.get('dosha_probabilities')
        if probs:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>AI Predictions:</b>", styles['CustomSubheading']))
            for dosha, prob in probs.items():
                if prob is not None:
                    try:
                        prob_val = float(prob)
                        elements.append(Paragraph(f"{str(dosha).capitalize()}: {prob_val*100:.1f}%", styles['CustomBody']))
                    except (TypeError, ValueError):
                        pass
        
        return elements
    
    def _create_tongue_section(self, tongue_data, styles):
        """Create tongue analysis section"""
        elements = []
        
        elements.append(Paragraph("Tongue Analysis (Jihva Pariksha)", styles['CustomHeading']))
        
        if not tongue_data:
            elements.append(Paragraph("Tongue analysis data not available", styles['CustomBody']))
            return elements
        
        if tongue_data.get('features'):
            features = tongue_data['features']
            elements.append(Paragraph(f"<b>Color:</b> {features.get('color', 'N/A')}", styles['CustomBody']))
            elements.append(Paragraph(f"<b>Coating:</b> {features.get('coating', 'N/A')}", styles['CustomBody']))
            elements.append(Paragraph(f"<b>Texture:</b> {features.get('texture', 'N/A')}", styles['CustomBody']))
        else:
            elements.append(Paragraph("Tongue features not available", styles['CustomBody']))
        
        return elements
    
    def _create_symptom_section(self, symptom_data, styles):
        """Create symptom analysis section"""
        elements = []
        
        elements.append(Paragraph("Symptom Analysis", styles['CustomHeading']))
        
        if not symptom_data:
            elements.append(Paragraph("Symptom analysis data not available", styles['CustomBody']))
            return elements
        
        if symptom_data.get('symptoms'):
            symptoms = symptom_data['symptoms']
            if isinstance(symptoms, list) and len(symptoms) > 0:
                elements.append(Paragraph("<b>Reported Symptoms:</b>", styles['CustomSubheading']))
                for symptom in symptoms[:10]:
                    if symptom:
                        elements.append(Paragraph(f"• {str(symptom)}", styles['CustomBody']))
            else:
                elements.append(Paragraph("No symptoms reported", styles['CustomBody']))
        else:
            elements.append(Paragraph("No symptoms reported", styles['CustomBody']))
        
        return elements
    
    def _create_fusion_section(self, fusion_data, styles):
        """Create fusion analysis section"""
        elements = []
        
        elements.append(Paragraph("AI Fusion Analysis", styles['CustomHeading']))
        
        # Weights used
        if fusion_data.get('weights_used'):
            weights = fusion_data['weights_used']
            text = f"""
            Our advanced AI system combines multiple diagnostic methods with weighted analysis:
            """
            elements.append(Paragraph(text, styles['CustomBody']))
            
            for modality, weight in weights.items():
                elements.append(Paragraph(f"• {modality.capitalize()}: {weight*100:.0f}%", styles['CustomBody']))
        
        # Source contributions
        if fusion_data.get('sources'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>Individual Modality Predictions:</b>", styles['CustomSubheading']))
            
            for modality, scores in fusion_data['sources'].items():
                # Skip if all scores are 0
                if not any(v > 0 for v in scores.values()):
                    continue
                    
                elements.append(Paragraph(f"<b>{modality.capitalize()}:</b>", styles['CustomBody']))
                for dosha, score in scores.items():
                    elements.append(Paragraph(f"  {dosha.capitalize()}: {score*100:.1f}%", styles['CustomBody']))
        
        return elements
    
    def _create_recommendations(self, data, styles):
        """Create recommendations section"""
        elements = []
        
        elements.append(Paragraph("Personalized Recommendations", styles['CustomHeading']))
        
        recommendations = data.get('recommendations', {})
        
        if not recommendations:
            elements.append(Paragraph("No specific recommendations available at this time.", styles['CustomBody']))
            return elements
        
        # Dietary recommendations
        if recommendations.get('dietary'):
            dietary = recommendations['dietary']
            if isinstance(dietary, list) and len(dietary) > 0:
                elements.append(Paragraph("<b>Dietary Guidelines:</b>", styles['CustomSubheading']))
                for rec in dietary[:8]:
                    if rec:  # Skip None or empty strings
                        elements.append(Paragraph(f"• {str(rec)}", styles['CustomBody']))
                elements.append(Spacer(1, 0.1*inch))
        
        # Lifestyle recommendations
        if recommendations.get('lifestyle'):
            lifestyle = recommendations['lifestyle']
            if isinstance(lifestyle, list) and len(lifestyle) > 0:
                elements.append(Paragraph("<b>Lifestyle Modifications:</b>", styles['CustomSubheading']))
                for rec in lifestyle[:8]:
                    if rec:  # Skip None or empty strings
                        elements.append(Paragraph(f"• {str(rec)}", styles['CustomBody']))
                elements.append(Spacer(1, 0.1*inch))
        
        # Yoga recommendations
        if recommendations.get('yoga'):
            yoga = recommendations['yoga']
            if isinstance(yoga, list) and len(yoga) > 0:
                elements.append(Paragraph("<b>Yoga & Exercise:</b>", styles['CustomSubheading']))
                for rec in yoga[:6]:
                    if rec:  # Skip None or empty strings
                        elements.append(Paragraph(f"• {str(rec)}", styles['CustomBody']))
        
        return elements
    
    def _create_remedies_section(self, remedies, styles):
        """Create home remedies section"""
        elements = []
        
        elements.append(Paragraph("Ayurvedic Home Remedies", styles['CustomHeading']))
        
        # Handle both list and detailed remedy formats
        if isinstance(remedies, list):
            if remedies and isinstance(remedies[0], dict):
                # Detailed remedies with name, ingredients, etc.
                for remedy in remedies[:5]:
                    elements.append(Paragraph(f"<b>{remedy.get('name', 'Remedy')}</b>", styles['CustomSubheading']))
                    
                    if remedy.get('ingredients'):
                        elements.append(Paragraph("<b>Ingredients:</b>", styles['CustomBody']))
                        for ing in remedy['ingredients'][:5]:
                            elements.append(Paragraph(f"• {ing}", styles['CustomBody']))
                    
                    if remedy.get('preparation'):
                        elements.append(Paragraph(f"<b>Preparation:</b> {remedy['preparation']}", styles['CustomBody']))
                    
                    if remedy.get('usage'):
                        elements.append(Paragraph(f"<b>Usage:</b> {remedy['usage']}", styles['CustomBody']))
                    
                    if remedy.get('benefits'):
                        elements.append(Paragraph(f"<b>Benefits:</b> {remedy['benefits']}", styles['CustomBody']))
                    
                    elements.append(Spacer(1, 0.1*inch))
            else:
                # Simple list of remedies
                for remedy in remedies[:10]:
                    elements.append(Paragraph(f"• {remedy}", styles['CustomBody']))
        
        return elements
    
    def _create_disclaimer(self, styles):
        """Create disclaimer section"""
        elements = []
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Important Disclaimer", styles['CustomHeading']))
        
        disclaimer_text = """
        This report is generated by AayurAI's artificial intelligence system and is intended for 
        informational and educational purposes only. It should not be considered as medical advice, 
        diagnosis, or treatment. Always consult with a qualified healthcare professional or certified 
        Ayurvedic practitioner before making any changes to your health regimen. The recommendations 
        provided are based on traditional Ayurvedic principles and AI analysis, but individual results 
        may vary. If you have any medical conditions or concerns, please seek professional medical attention.
        """
        
        elements.append(Paragraph(disclaimer_text, styles['CustomBody']))
        
        return elements
    
    def _add_page_number(self, canvas, doc):
        """Add page number to each page"""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(7.5*inch, 0.5*inch, text)
        canvas.drawString(1*inch, 0.5*inch, "AayurAI - Ayurvedic Health Assessment")
        canvas.restoreState()


# Global instance
pdf_report_service = PDFReportService()
