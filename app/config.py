"""Configuration management for the SMS-Agent."""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-nano", env="OPENAI_MODEL")
    openai_web_search_model: str = Field(default="gpt-4.1-nano", env="OPENAI_WEB_SEARCH_MODEL")
    pdf_finder_model: str = Field(default="gpt-4o-mini", env="PDF_FINDER_MODEL")
    openai_web_search_timeout: int = Field(default=60, env="OPENAI_WEB_SEARCH_TIMEOUT")
    
    # Google AI Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    google_model: str = Field(default="gemini-2.5-flash-preview-05-20", env="GOOGLE_MODEL")
    
    # Science Made Simple API Configuration
    sms_api_key: str = Field(default="4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5", env="SMS_API_KEY")
    
    # Email Configuration
    email_user: Optional[str] = Field(default=None, env="EMAIL_USER")
    email_password: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    
    # WhatsApp Configuration (WhatsApp Business API)
    whatsapp_api_url: Optional[str] = Field(default=None, env="WHATSAPP_API_URL")
    whatsapp_token: Optional[str] = Field(default=None, env="WHATSAPP_TOKEN")
    whatsapp_phone_number_id: Optional[str] = Field(default=None, env="WHATSAPP_PHONE_NUMBER_ID")
    
    # Twilio Configuration (Alternative for WhatsApp)
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_whatsapp_number: Optional[str] = Field(default=None, env="TWILIO_WHATSAPP_NUMBER")
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # DynamoDB Table Names
    dynamodb_sessions_table: str = Field(
        default="sms-agent-sessions", 
        env="DYNAMODB_SESSIONS_TABLE"
    )
    dynamodb_content_cache_table: str = Field(
        default="sms-agent-content-cache", 
        env="DYNAMODB_CONTENT_CACHE_TABLE"
    )
    
    # Agent Configuration
    max_concurrent_tools: int = Field(default=3, env="MAX_CONCURRENT_TOOLS")
    tool_execution_timeout: int = Field(default=300, env="TOOL_EXECUTION_TIMEOUT")
    enable_content_caching: bool = Field(default=True, env="ENABLE_CONTENT_CACHING")
    session_ttl_hours: int = Field(default=24, env="SESSION_TTL_HOURS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # API Configuration
    api_host: str = Field(default="localhost", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Supported file types for course content
    supported_file_types: List[str] = [
        ".pdf", ".pptx", ".docx", ".txt", ".md"
    ]
    
    # Maximum file size (in bytes) - 50MB default
    max_file_size: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 