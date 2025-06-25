# WhatsApp Business API Setup Guide

This guide will walk you through setting up WhatsApp Business API for your SMS Agent from scratch.

## 🎯 Overview

WhatsApp Business API allows you to send WhatsApp messages programmatically. It's more powerful than Twilio's sandbox but requires more setup.

## 📋 Prerequisites

- Valid business (for verification)
- Phone number dedicated to WhatsApp Business
- Meta Business Account
- Facebook Developer Account

## 🚀 Step-by-Step Setup

### Step 1: Create Meta Business Account

1. **Go to Meta Business**: https://business.facebook.com/
2. **Click "Create Account"**
3. **Fill in business details:**
   - Business name
   - Your name
   - Business email
4. **Verify your business information**

### Step 2: Create Developer App

1. **Go to Meta for Developers**: https://developers.facebook.com/
2. **Click "My Apps" → "Create App"**
3. **Choose "Business" as app type**
4. **Fill in app details:**
   - App name (e.g., "SMS Agent WhatsApp")
   - Contact email
   - Select your business account
5. **Click "Create App"**

### Step 3: Add WhatsApp Product

1. **In your app dashboard, scroll to "Add Products"**
2. **Find "WhatsApp" and click "Set Up"**
3. **WhatsApp will be added to your app**

### Step 4: Get Phone Number

1. **In WhatsApp settings, go to "API Setup"**
2. **You'll see a temporary phone number for testing**
3. **For production, you'll need to add your own phone number:**
   - Click "Add phone number"
   - Verify ownership
   - Complete business verification

### Step 5: Get Your Credentials

You need these 3 pieces of information:

#### 1. Phone Number ID
- Found in **WhatsApp → API Setup**
- Looks like: `123456789012345`

#### 2. Access Token
- Found in **WhatsApp → API Setup**
- Click "Generate Access Token"
- **Important:** Save this token securely!

#### 3. API URL
- Usually: `https://graph.facebook.com/v17.0`
- Check Meta's documentation for the latest version

### Step 6: Configure Webhook (Optional)

For receiving message status and replies:

1. **In WhatsApp → Configuration**
2. **Set Webhook URL** (your server endpoint)
3. **Set Verify Token** (random string you choose)
4. **Subscribe to webhook fields:**
   - messages
   - message_deliveries
   - message_reads

## 🔧 SMS Agent Configuration

Once you have your credentials, run the setup script:

```bash
python setup_whatsapp_business.py
```

Or manually add to your `.env` file:

```bash
# WhatsApp Business API Configuration
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

## 🧪 Testing Your Setup

### Test 1: Send to Your Own Number

```python
from app.tools.messaging_tool import MessagingTool
import asyncio

async def test_whatsapp():
    tool = MessagingTool()
    result = await tool.execute({
        "message_type": "whatsapp",
        "recipient": "+1234567890",  # Your phone number
        "message": "Hello! This is a test from SMS Agent."
    })
    print(result.dict())

asyncio.run(test_whatsapp())
```

### Test 2: Run Examples

```bash
python examples/messaging_examples.py
```

## ⚠️ Important Limitations

### Development Phase
- Can only message numbers you've added to your app
- Limited to 5 phone numbers
- 1000 conversations per month

### Production Phase
- Requires business verification
- Message templates must be approved
- Higher rate limits available
- Can message any valid WhatsApp number

## 🚀 Going to Production

### 1. Business Verification
- Complete business verification in Meta Business Manager
- Provide business documents
- Verify business address and phone

### 2. Message Templates
- Create message templates for common use cases
- Submit for approval (takes 24-48 hours)
- Templates are required for outbound messages

### 3. Request Higher Limits
- Request increased conversation limits
- Provide use case documentation
- Show compliance with WhatsApp policies

## 📊 Message Types

### 1. Template Messages
- For initiating conversations
- Must be pre-approved
- Used for notifications, alerts, etc.

### 2. Free-form Messages  
- For ongoing conversations
- Can be sent within 24 hours of user message
- No approval needed

## 🛠️ Advanced Configuration

### Webhook Setup

If you want to receive message status updates:

```python
# In your FastAPI app
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    # Process webhook data
    return {"status": "ok"}
```

### Message Templates Example

Create templates in Meta Business Manager:

```json
{
  "name": "course_reminder",
  "category": "UTILITY",
  "language": "en_US",
  "components": [
    {
      "type": "BODY",
      "text": "Hi {{1}}, your {{2}} class is starting in {{3}} minutes!"
    }
  ]
}
```

## 🔍 Troubleshooting

### Common Issues

**1. "Invalid phone number ID"**
- Check you're using the correct Phone Number ID from API Setup
- Ensure the phone number is verified

**2. "Invalid access token"**
- Regenerate access token in Meta Developer Console
- Check token hasn't expired

**3. "Recipient not found"**
- In development: Add recipient to your test numbers
- In production: Ensure number is valid WhatsApp number

**4. "Template not found"**
- Create and approve message templates
- Use template name exactly as registered

### Rate Limits

- **Development**: 50 messages per day
- **Production**: Based on your tier (1K-100K+ per day)

### Message Delivery

- Check WhatsApp Business Manager for delivery status
- Messages show as delivered/read/failed
- Failed messages include error reasons

## 💰 Pricing

### Meta's Pricing (as of 2024)
- **Authentication**: $0.005-0.009 per message
- **Marketing**: $0.025-0.165 per message  
- **Utility**: $0.005-0.08 per message
- **Service**: Free within 24-hour window

*Prices vary by country and message type*

## 🔗 Useful Links

- **Meta Business**: https://business.facebook.com/
- **Developer Docs**: https://developers.facebook.com/docs/whatsapp/
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp/getting-started/
- **Message Templates**: https://developers.facebook.com/docs/whatsapp/message-templates/
- **Pricing**: https://developers.facebook.com/docs/whatsapp/pricing/

## 🆘 Need Help?

1. **Meta Developer Community**: https://developers.facebook.com/community/
2. **WhatsApp Business Support**: Through Meta Business Manager
3. **SMS Agent Issues**: Check our troubleshooting guide or create an issue

## 🔒 Security Best Practices

- Store access tokens securely (environment variables)
- Regularly rotate access tokens
- Monitor API usage for unusual activity
- Use webhook signatures to verify requests
- Implement rate limiting in your application
- Keep your Meta Business account secure with 2FA 