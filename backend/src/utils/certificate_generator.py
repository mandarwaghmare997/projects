"""
Certificate PDF Generator for Qryti Learn
Creates professional PDF certificates for course completion
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, white, gold
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
import uuid

class CertificateGenerator:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 0.75 * inch
        
        # Colors
        self.primary_color = Color(0.2, 0.4, 0.8)  # Blue
        self.secondary_color = Color(0.8, 0.6, 0.2)  # Gold
        self.text_color = Color(0.2, 0.2, 0.2)  # Dark gray
        
        # Fonts and styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for the certificate"""
        
        # Certificate title style
        self.title_style = ParagraphStyle(
            'CertificateTitle',
            parent=self.styles['Heading1'],
            fontSize=36,
            textColor=self.primary_color,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CertificateSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=self.text_color,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica'
        )
        
        # Recipient name style
        self.name_style = ParagraphStyle(
            'RecipientName',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=self.secondary_color,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        # Course name style
        self.course_style = ParagraphStyle(
            'CourseName',
            parent=self.styles['Heading2'],
            fontSize=20,
            textColor=self.primary_color,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CertificateBody',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=self.text_color,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica'
        )
        
        # Footer style
        self.footer_style = ParagraphStyle(
            'CertificateFooter',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
    
    def generate_certificate(self, certificate_data, output_path):
        """
        Generate a PDF certificate
        
        Args:
            certificate_data (dict): Certificate information
            output_path (str): Path to save the PDF file
        """
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Build the certificate content
        story = []
        
        # Add decorative border (using canvas)
        def add_border(canvas, doc):
            canvas.saveState()
            
            # Outer border
            canvas.setStrokeColor(self.primary_color)
            canvas.setLineWidth(3)
            canvas.rect(
                self.margin/2, 
                self.margin/2, 
                self.page_width - self.margin, 
                self.page_height - self.margin
            )
            
            # Inner decorative border
            canvas.setStrokeColor(self.secondary_color)
            canvas.setLineWidth(1)
            canvas.rect(
                self.margin/2 + 10, 
                self.margin/2 + 10, 
                self.page_width - self.margin - 20, 
                self.page_height - self.margin - 20
            )
            
            canvas.restoreState()
        
        # Header spacer
        story.append(Spacer(1, 0.5 * inch))
        
        # Certificate title
        title = Paragraph("CERTIFICATE OF COMPLETION", self.title_style)
        story.append(title)
        
        # Subtitle
        subtitle = Paragraph("This is to certify that", self.subtitle_style)
        story.append(subtitle)
        
        # Recipient name
        recipient_name = Paragraph(certificate_data['recipient_name'], self.name_style)
        story.append(recipient_name)
        
        # Completion text
        completion_text = Paragraph("has successfully completed the course", self.body_style)
        story.append(completion_text)
        
        # Course name
        course_name = Paragraph(certificate_data['course_name'], self.course_style)
        story.append(course_name)
        
        # Course details
        if certificate_data.get('final_score'):
            score_text = f"with a final score of {certificate_data['final_score']}%"
            score_para = Paragraph(score_text, self.body_style)
            story.append(score_para)
        
        # Completion date
        completion_date = certificate_data.get('completion_date', datetime.now())
        if isinstance(completion_date, str):
            date_text = f"Completed on {completion_date}"
        else:
            date_text = f"Completed on {completion_date.strftime('%B %d, %Y')}"
        
        date_para = Paragraph(date_text, self.body_style)
        story.append(date_para)
        
        # Add spacer before certificate details
        story.append(Spacer(1, 0.5 * inch))
        
        # Certificate details table
        cert_details = [
            ['Certificate ID:', certificate_data['certificate_id']],
            ['Issued by:', 'Qryti Learn - ISO/IEC 42001 AI Management Systems'],
            ['Verification URL:', f"https://qryti.com/verify/{certificate_data['certificate_id']}"]
        ]
        
        details_table = Table(cert_details, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.text_color),
            ('TEXTCOLOR', (1, 0), (1, -1), self.primary_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(details_table)
        
        # Footer spacer
        story.append(Spacer(1, 0.3 * inch))
        
        # Footer text
        footer_text = "This certificate verifies the successful completion of the specified course and demonstrates competency in ISO/IEC 42001 AI Management Systems."
        footer_para = Paragraph(footer_text, self.footer_style)
        story.append(footer_para)
        
        # Build the PDF with border
        doc.build(story, onFirstPage=add_border, onLaterPages=add_border)
        
        return output_path
    
    def generate_certificate_for_user(self, user, course, certificate_id, final_score=None, completion_date=None):
        """
        Generate certificate for a specific user and course
        
        Args:
            user: User object
            course: Course object  
            certificate_id: Unique certificate identifier
            final_score: Final score percentage
            completion_date: Date of completion
        """
        
        # Prepare certificate data
        certificate_data = {
            'recipient_name': user.full_name or f"{user.first_name} {user.last_name}",
            'course_name': course.title,
            'certificate_id': certificate_id,
            'final_score': final_score,
            'completion_date': completion_date or datetime.now(),
            'course_description': course.description
        }
        
        # Create certificates directory if it doesn't exist
        certificates_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'certificates')
        os.makedirs(certificates_dir, exist_ok=True)
        
        # Generate filename
        filename = f"certificate_{certificate_id}.pdf"
        output_path = os.path.join(certificates_dir, filename)
        
        # Generate the certificate
        return self.generate_certificate(certificate_data, output_path)

# Utility function for easy access
def create_certificate(user, course, certificate_id, final_score=None, completion_date=None):
    """
    Create a certificate PDF for the given user and course
    """
    generator = CertificateGenerator()
    return generator.generate_certificate_for_user(
        user, course, certificate_id, final_score, completion_date
    )

