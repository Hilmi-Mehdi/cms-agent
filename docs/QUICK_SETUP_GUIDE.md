# 🚀 Quick Setup Guide for Messaging Tool

## Option 1: Interactive Setup (Recommended)

Run the interactive setup script:

```bash
python setup_messaging.py
```

This script will:
- ✅ Guide you through configuration
- ✅ Test your email connection
- ✅ Create the .env file automatically
- ✅ Provide helpful instructions

## Option 2: Manual Setup

### Step 1: Gmail Email Setup (5 minutes)

1. **Enable 2-Factor Authentication:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable "2-Step Verification"

2. **Generate App Password:**
   - In Security settings, click "App passwords"
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Add to your .env file:**
   ```bash
   EMAIL_USER=your.email@gmail.com
   EMAIL_PASSWORD=your_16_character_app_password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

### Step 2: Twilio WhatsApp Setup (10 minutes)

1. **Sign up for Twilio:**
   - Go to [Twilio.com](https://www.twilio.com/)
   - Create free account

2. **Get Credentials:**
   - Go to Twilio Console
   - Copy Account SID and Auth Token

3. **Join WhatsApp Sandbox:**
   - Go to Messaging → Try it out → WhatsApp
   - Send join code to +1 415 523 8886
   - Example: Send "join <code>" to the number

4. **Add to your .env file:**
   ```bash
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_NUMBER=+14155238886
   ```

### Step 3: Test Configuration

```bash
python examples/messaging_examples.py
```

## 🔧 Complete .env File Example

Create a `.env` file in your project root:

```bash
# Core API Keys (required)
OPENAI_API_KEY=sk-your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# Email Configuration
EMAIL_USER=your.email@gmail.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# WhatsApp via Twilio
TWILIO_ACCOUNT_SID=AC1234567890abcdef
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886

# Other settings
SMS_API_KEY=4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5
AWS_REGION=us-east-1
```

## 🧪 Quick Test

Send a test email:

```python
from app.tools.messaging_tool import MessagingTool
import asyncio

async def test():
    tool = MessagingTool()
    result = await tool.execute({
        "message_type": "email",
        "recipient": "your.test@email.com",
        "subject": "Test from SMS Agent",
        "message": "Hello! This is a test message."
    })
    print(result.dict())

asyncio.run(test())
```

## 📱 Provider-Specific Instructions

### Gmail
- **Must use app password** (not regular password)
- Enable 2FA first
- Get app password from: https://myaccount.google.com/apppasswords

### Outlook/Hotmail
```bash
EMAIL_USER=your.email@outlook.com
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### WhatsApp Business API (Production)
```bash
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_TOKEN=your_permanent_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

## ❓ Common Issues

**Email "Authentication failed":**
- ✅ Use app password, not regular password
- ✅ Enable 2-factor authentication first

**WhatsApp "Invalid phone number":**
- ✅ Include country code: +1234567890
- ✅ For Twilio sandbox: recipient must join first

**"Missing environment variables":**
- ✅ Create .env file in project root
- ✅ Restart your application after adding variables

## 🎯 Next Steps

1. **Run interactive setup:** `python setup_messaging.py`
2. **Test configuration:** `python examples/messaging_examples.py`
3. **Read full docs:** `docs/MESSAGING_TOOL_SETUP.md`
4. **Start messaging!** The tool is now ready to use

## 🔒 Security Reminders

- Never commit .env files to git
- Use app passwords for email
- Keep API keys secure
- Regularly rotate credentials 