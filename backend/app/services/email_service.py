"""
Email Service
Handles sending emails for verification, password reset, etc.
"""

import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending verification and notification emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.email_from_name = settings.EMAIL_FROM_NAME
        self.frontend_url = settings.FRONTEND_URL
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.email_from_name} <{self.email_from}>"
            message['To'] = to_email
            
            # Add text part
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                message.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_verification_email(self, to_email: str, token: str) -> bool:
        """
        Send email verification email
        
        Args:
            to_email: User's email address
            token: Verification token
            
        Returns:
            True if email sent successfully
        """
        verification_url = f"{self.frontend_url}/verify-email?token={token}"
        
        subject = "Verify Your AayurAI Account"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8fafc;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 15px 30px;
                    background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #64748b;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌿 AayurAI</h1>
                    <p>Welcome to Personalized Ayurvedic Care</p>
                </div>
                <div class="content">
                    <h2>Verify Your Email Address</h2>
                    <p>Thank you for registering with AayurAI! To complete your registration and start your journey to better health, please verify your email address.</p>
                    
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #0ea5e9;">{verification_url}</p>
                    
                    <p><strong>This link will expire in 24 hours.</strong></p>
                    
                    <p>If you didn't create an account with AayurAI, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2026 AayurAI - AI-Powered Ayurvedic Diagnostics</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to AayurAI!
        
        Thank you for registering. To complete your registration, please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account with AayurAI, you can safely ignore this email.
        
        © 2026 AayurAI - AI-Powered Ayurvedic Diagnostics
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_password_reset_email(self, to_email: str, token: str) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: User's email address
            token: Reset token
            
        Returns:
            True if email sent successfully
        """
        reset_url = f"{self.frontend_url}/reset-password?token={token}"
        
        subject = "Reset Your AayurAI Password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8fafc;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 15px 30px;
                    background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .warning {{
                    background: #fee2e2;
                    border-left: 4px solid #ef4444;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #64748b;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌿 AayurAI</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #0ea5e9;">{reset_url}</p>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul>
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this, please ignore this email</li>
                            <li>Your password will not change until you create a new one</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>© 2026 AayurAI - AI-Powered Ayurvedic Diagnostics</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        We received a request to reset your password. Click the link below to create a new password:
        
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email. Your password will not change until you create a new one.
        
        © 2026 AayurAI - AI-Powered Ayurvedic Diagnostics
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_welcome_email(self, to_email: str, full_name: str) -> bool:
        """
        Send welcome email after verification
        
        Args:
            to_email: User's email address
            full_name: User's full name
            
        Returns:
            True if email sent successfully
        """
        subject = "Welcome to AayurAI! 🌿"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8fafc;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .feature {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid #10b981;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #64748b;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌿 Welcome to AayurAI!</h1>
                    <p>Your Journey to Better Health Begins</p>
                </div>
                <div class="content">
                    <h2>Hello {full_name}! 👋</h2>
                    <p>Your email has been verified successfully! We're excited to have you join our community.</p>
                    
                    <h3>What You Can Do Now:</h3>
                    
                    <div class="feature">
                        <strong>🔍 Complete Assessment</strong>
                        <p>Take our comprehensive Ayurvedic assessment using pulse analysis, tongue diagnosis, and symptom evaluation.</p>
                    </div>
                    
                    <div class="feature">
                        <strong>🎤 Voice AI Assistant</strong>
                        <p>Chat with our multilingual AI assistant in your preferred language for personalized health guidance.</p>
                    </div>
                    
                    <div class="feature">
                        <strong>📊 Track Your Progress</strong>
                        <p>View your consultation history and track your health journey over time.</p>
                    </div>
                    
                    <div class="feature">
                        <strong>🌱 Personalized Recommendations</strong>
                        <p>Get customized Ayurvedic remedies, diet plans, and lifestyle suggestions based on your dosha.</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{self.frontend_url}/assessment" style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #0ea5e9, #8b5cf6); color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">Start Your Assessment</a>
                    </p>
                </div>
                <div class="footer">
                    <p>© 2026 AayurAI - AI-Powered Ayurvedic Diagnostics</p>
                    <p>Need help? Contact us at support@aayurai.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to AayurAI!
        
        Hello {full_name}!
        
        Your email has been verified successfully! We're excited to have you join our community.
        
        What You Can Do Now:
        
        🔍 Complete Assessment
        Take our comprehensive Ayurvedic assessment using pulse analysis, tongue diagnosis, and symptom evaluation.
        
        🎤 Voice AI Assistant
        Chat with our multilingual AI assistant in your preferred language for personalized health guidance.
        
        📊 Track Your Progress
        View your consultation history and track your health journey over time.
        
        🌱 Personalized Recommendations
        Get customized Ayurvedic remedies, diet plans, and lifestyle suggestions based on your dosha.
        
        Start your assessment: {self.frontend_url}/assessment
        
        © 2026 AayurAI - AI-Powered Ayurvedic Diagnostics
        Need help? Contact us at support@aayurai.com
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)


# Singleton instance
email_service = EmailService()
