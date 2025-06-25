"""Messaging tool for sending emails and WhatsApp messages."""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
import requests
from typing import Dict, Any, List, Optional
import asyncio
import aiofiles

from app.tools.base_tool import BaseTool, ToolDefinition, ToolParameter
from app.models.schemas import ToolResult


class MessagingTool(BaseTool):
    """Tool for sending emails and WhatsApp messages."""
    
    def __init__(self):
        super().__init__()
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        
        # WhatsApp configuration (using WhatsApp Business API or Twilio)
        self.whatsapp_api_url = os.getenv("WHATSAPP_API_URL", "")
        self.whatsapp_token = os.getenv("WHATSAPP_TOKEN", "")
        self.whatsapp_phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        
        # Twilio configuration (alternative for WhatsApp)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
    
    def get_definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="messaging",
            description="Send emails and WhatsApp messages to recipients",
            parameters=[
                ToolParameter(
                    name="message_type",
                    type="string",
                    description="Type of message to send",
                    required=True,
                    enum=["email", "whatsapp"]
                ),
                ToolParameter(
                    name="recipient",
                    type="string",
                    description="Recipient email address or phone number (with country code for WhatsApp)",
                    required=True
                ),
                ToolParameter(
                    name="subject",
                    type="string",
                    description="Subject line (for emails only)",
                    required=False
                ),
                ToolParameter(
                    name="message",
                    type="string",
                    description="Message content to send",
                    required=True
                ),
                ToolParameter(
                    name="message_format",
                    type="string",
                    description="Format of the message",
                    required=False,
                    default="text",
                    enum=["text", "html"]
                ),
                ToolParameter(
                    name="attachments",
                    type="array",
                    description="List of file paths to attach (emails only)",
                    required=False
                ),
                ToolParameter(
                    name="priority",
                    type="string",
                    description="Message priority level",
                    required=False,
                    default="normal",
                    enum=["low", "normal", "high"]
                ),
                ToolParameter(
                    name="sender_name",
                    type="string",
                    description="Display name for the sender",
                    required=False
                )
            ]
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the messaging action."""
        message_type = parameters["message_type"]
        recipient = parameters["recipient"]
        message = parameters["message"]
        
        try:
            if message_type == "email":
                result = await self._send_email(parameters)
            elif message_type == "whatsapp":
                result = await self._send_whatsapp(parameters)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unsupported message type: {message_type}"
                )
            
            return result
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to send {message_type} message: {str(e)}"
            )
    
    async def _send_email(self, parameters: Dict[str, Any]) -> ToolResult:
        """Send an email message."""
        recipient = parameters["recipient"]
        subject = parameters.get("subject", "Message from SMS Agent")
        message = parameters["message"]
        message_format = parameters.get("message_format", "text")
        attachments = parameters.get("attachments", [])
        priority = parameters.get("priority", "normal")
        sender_name = parameters.get("sender_name", "SMS Agent")
        
        if not self.email_user or not self.email_password:
            return ToolResult(
                success=False,
                error="Email credentials not configured. Please set EMAIL_USER and EMAIL_PASSWORD environment variables."
            )
        
        try:
            # Create message
            msg = MIMEMultipart('alternative' if message_format == "html" else 'mixed')
            msg['From'] = f"{sender_name} <{self.email_user}>"
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Set priority
            if priority == "high":
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            elif priority == "low":
                msg['X-Priority'] = '5'
                msg['X-MSMail-Priority'] = 'Low'
            
            # Create message body
            if message_format == "html":
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Add attachments
            for attachment_path in attachments:
                if os.path.isfile(attachment_path):
                    await self._add_attachment(msg, attachment_path)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            return ToolResult(
                success=True,
                data={
                    "message_type": "email",
                    "recipient": recipient,
                    "subject": subject,
                    "message_length": len(message),
                    "attachments_count": len(attachments),
                    "priority": priority
                },
                agent_notes=f"Email sent successfully to {recipient}"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to send email: {str(e)}"
            )
    
    async def _add_attachment(self, msg: MIMEMultipart, file_path: str) -> None:
        """Add file attachment to email."""
        try:
            async with aiofiles.open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(await attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            msg.attach(part)
        except Exception as e:
            # Log the error but don't fail the entire email
            print(f"Warning: Failed to attach file {file_path}: {str(e)}")
    
    async def _send_whatsapp(self, parameters: Dict[str, Any]) -> ToolResult:
        """Send a WhatsApp message."""
        recipient = parameters["recipient"]
        message = parameters["message"]
        
        # Normalize phone number (ensure it starts with + and country code)
        if not recipient.startswith('+'):
            return ToolResult(
                success=False,
                error="WhatsApp phone number must include country code (e.g., +1234567890)"
            )
        
        # Try WhatsApp Business API first, then fall back to Twilio
        if self.whatsapp_api_url and self.whatsapp_token:
            return await self._send_whatsapp_business_api(recipient, message)
        elif self.twilio_account_sid and self.twilio_auth_token:
            return await self._send_whatsapp_twilio(recipient, message)
        else:
            return ToolResult(
                success=False,
                error="WhatsApp configuration not found. Please configure either WhatsApp Business API or Twilio credentials."
            )
    
    async def _send_whatsapp_business_api(self, recipient: str, message: str) -> ToolResult:
        """Send WhatsApp message using WhatsApp Business API."""
        try:
            url = f"{self.whatsapp_api_url}/{self.whatsapp_phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient.replace('+', ''),
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            
            return ToolResult(
                success=True,
                data={
                    "message_type": "whatsapp",
                    "recipient": recipient,
                    "message_length": len(message),
                    "provider": "whatsapp_business_api",
                    "message_id": response_data.get("messages", [{}])[0].get("id")
                },
                agent_notes=f"WhatsApp message sent successfully to {recipient}"
            )
            
        except requests.exceptions.RequestException as e:
            return ToolResult(
                success=False,
                error=f"WhatsApp Business API request failed: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"WhatsApp Business API error: {str(e)}"
            )
    
    async def _send_whatsapp_twilio(self, recipient: str, message: str) -> ToolResult:
        """Send WhatsApp message using Twilio."""
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            twilio_message = client.messages.create(
                body=message,
                from_=f"whatsapp:{self.twilio_whatsapp_number}",
                to=f"whatsapp:{recipient}"
            )
            
            return ToolResult(
                success=True,
                data={
                    "message_type": "whatsapp",
                    "recipient": recipient,
                    "message_length": len(message),
                    "provider": "twilio",
                    "message_sid": twilio_message.sid,
                    "status": twilio_message.status
                },
                agent_notes=f"WhatsApp message sent successfully to {recipient} via Twilio"
            )
            
        except ImportError:
            return ToolResult(
                success=False,
                error="Twilio library not installed. Please install with: pip install twilio"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Twilio WhatsApp error: {str(e)}"
            )
    
    def _suggest_next_tools(self, message_type: str) -> List[str]:
        """Suggest follow-up tools based on message type."""
        if message_type == "email":
            return ["content_analyzer", "file_processor"]
        elif message_type == "whatsapp":
            return ["content_analyzer"]
        return [] 