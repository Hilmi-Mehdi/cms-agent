# Messaging Tool Setup Guide

The messaging tool allows the SMS Agent to send both emails and WhatsApp messages. This guide will help you configure the necessary services and environment variables.

## Features

- Send emails with attachments
- Send WhatsApp messages via WhatsApp Business API or Twilio
- Support for HTML and plain text messages
- Email priority settings
- Async message delivery

## Configuration

### Email Setup

To send emails, you'll need to configure SMTP settings in your environment variables:

```bash
# Gmail configuration (recommended)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password  # Use app password, not regular password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Other email providers
# Outlook: smtp-mail.outlook.com:587
# Yahoo: smtp.mail.yahoo.com:587
```

#### Gmail Setup Instructions

1. Enable 2-factor authentication on your Gmail account
2. Go to Google Account settings > Security > 2-Step Verification
3. Generate an "App Password" for the SMS Agent
4. Use this app password in the `EMAIL_PASSWORD` environment variable

### WhatsApp Setup

You have two options for WhatsApp messaging:

#### Option 1: WhatsApp Business API (Recommended)

```bash
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_TOKEN=your_whatsapp_business_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

To get these credentials:
1. Sign up for WhatsApp Business API
2. Create a Meta Business Account
3. Set up a WhatsApp Business Account
4. Get your access token and phone number ID from the Meta Developer Console

#### Option 2: Twilio (Alternative)

```bash
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886  # Twilio sandbox number
```

To get Twilio credentials:
1. Sign up for a Twilio account
2. Get your Account SID and Auth Token from the Twilio Console
3. Enable WhatsApp sandbox for testing

## Dependencies

The messaging tool requires additional Python packages. Install them with:

```bash
pip install aiofiles requests twilio
```

## Usage Examples

### Send Email

```python
from app.tools.messaging_tool import MessagingTool

messaging_tool = MessagingTool()

# Send simple text email
result = await messaging_tool.execute({
    "message_type": "email",
    "recipient": "user@example.com",
    "subject": "Hello from SMS Agent",
    "message": "This is a test email from the SMS Agent.",
    "sender_name": "SMS Agent"
})

# Send HTML email with attachments
result = await messaging_tool.execute({
    "message_type": "email",
    "recipient": "user@example.com",
    "subject": "Course Materials",
    "message": "<h1>Course Materials</h1><p>Please find the attached files.</p>",
    "message_format": "html",
    "attachments": ["/path/to/file1.pdf", "/path/to/file2.docx"],
    "priority": "high",
    "sender_name": "SMS Agent"
})
```

### Send WhatsApp Message

```python
# Send WhatsApp message
result = await messaging_tool.execute({
    "message_type": "whatsapp",
    "recipient": "+1234567890",  # Include country code
    "message": "Hello! This is a message from SMS Agent."
})
```

### Using the Agent API

You can also use the messaging tool through the agent API:

```python
import requests

response = requests.post("http://localhost:8000/api/v1/agent/chat", json={
    "user_query": "Send an email to john@example.com with subject 'Meeting Reminder' and message 'Don't forget about our meeting tomorrow at 2 PM'",
    "context": {
        "messaging_preferences": {
            "sender_name": "SMS Agent",
            "priority": "normal"
        }
    }
})
```

## Security Notes

- Never commit your API keys or passwords to version control
- Use environment variables or secure secret management
- Enable 2-factor authentication on all accounts
- Use app passwords instead of regular passwords for email
- Regularly rotate your API tokens and passwords

## Troubleshooting

### Email Issues

1. **Authentication Error**: Make sure you're using an app password, not your regular password
2. **Connection Timeout**: Check your SMTP server and port settings
3. **Permission Denied**: Ensure 2-factor authentication is enabled and app password is correct

### WhatsApp Issues

1. **Invalid Phone Number**: Ensure phone numbers include country code (e.g., +1234567890)
2. **API Token Error**: Verify your WhatsApp Business API token is valid
3. **Twilio Sandbox**: For testing, make sure the recipient has joined your Twilio sandbox

### General Issues

1. **Missing Dependencies**: Install required packages with `pip install aiofiles requests twilio`
2. **Environment Variables**: Check that all required environment variables are set
3. **Network Issues**: Ensure your server can make outbound connections to email/WhatsApp services

## Rate Limits

- **Email**: Most providers have rate limits (e.g., Gmail: 500/day for free accounts)
- **WhatsApp Business API**: Varies by tier and approval status
- **Twilio**: Depends on your account type and phone number verification

## Advanced Configuration

### Custom SMTP Servers

You can use any SMTP server by configuring:

```bash
SMTP_SERVER=your.smtp.server.com
SMTP_PORT=587  # or 465 for SSL
```

### WhatsApp Templates

For production WhatsApp messaging, you'll need to use approved message templates. The current implementation supports simple text messages, but can be extended for templates.

### Error Handling

The messaging tool includes comprehensive error handling and will return detailed error messages for troubleshooting. 