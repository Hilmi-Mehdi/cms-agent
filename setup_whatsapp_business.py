#!/usr/bin/env python3
"""
WhatsApp Business API setup for SMS Agent messaging tool.
This script helps configure WhatsApp Business API credentials.
"""

import os
import requests

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    """Print a section header."""
    print(f"\n📋 {title}")
    print("-" * 40)

def get_user_input(prompt, default=None, sensitive=False):
    """Get user input with optional default and sensitive handling."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if sensitive:
        import getpass
        value = getpass.getpass(prompt)
    else:
        value = input(prompt).strip()
    
    return value if value else default

def test_whatsapp_credentials(api_url, token, phone_number_id):
    """Test WhatsApp Business API credentials."""
    print("🧪 Testing WhatsApp Business API credentials...")
    
    try:
        # Test API endpoint
        url = f"{api_url}/{phone_number_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Make a simple GET request to verify credentials
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ WhatsApp Business API credentials are valid!")
            return True
        elif response.status_code == 401:
            print("   ❌ Authentication failed - check your access token")
            return False
        elif response.status_code == 404:
            print("   ❌ Phone number ID not found - check your phone number ID")
            return False
        else:
            print(f"   ⚠️  API responded with status {response.status_code}")
            print("   This might still work - continuing setup...")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Could not test API connection: {e}")
        print("   This might be a network issue - continuing setup...")
        return True
    except Exception as e:
        print(f"   ❌ Error testing credentials: {e}")
        return False

def update_env_file(whatsapp_config):
    """Update .env file with WhatsApp Business API configuration."""
    env_exists = os.path.exists('.env')
    
    if env_exists:
        # Read existing content
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update existing WhatsApp settings or add new ones
        updated_lines = []
        whatsapp_keys = set(whatsapp_config.keys())
        found_keys = set()
        
        for line in lines:
            stripped = line.strip()
            if '=' in stripped and not stripped.startswith('#'):
                key = stripped.split('=')[0].strip()
                if key in whatsapp_config:
                    updated_lines.append(f"{key}={whatsapp_config[key]}\n")
                    found_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Add missing WhatsApp settings
        missing_keys = whatsapp_keys - found_keys
        if missing_keys:
            updated_lines.append("\n# WhatsApp Business API Configuration\n")
            for key in missing_keys:
                updated_lines.append(f"{key}={whatsapp_config[key]}\n")
        
        content = ''.join(updated_lines)
    else:
        # Create new .env file
        content = f"""# SMS Agent Configuration
# WhatsApp Business API Setup

# Core API Keys (add your actual keys)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# Email Configuration (Mailtrap)
EMAIL_USER=84d6fc1cf9741c
EMAIL_PASSWORD=86b7113a509df7
SMTP_SERVER=sandbox.smtp.mailtrap.io
SMTP_PORT=2525

# WhatsApp Business API Configuration
WHATSAPP_API_URL={whatsapp_config['WHATSAPP_API_URL']}
WHATSAPP_TOKEN={whatsapp_config['WHATSAPP_TOKEN']}
WHATSAPP_PHONE_NUMBER_ID={whatsapp_config['WHATSAPP_PHONE_NUMBER_ID']}

# Other Configuration
SMS_API_KEY=4b7e3d9a5c8f2a6d1e9b4c7f3a2d8e5
AWS_REGION=us-east-1
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error updating .env file: {e}")
        return False

def main():
    """Main setup function."""
    print_header("WhatsApp Business API Setup for SMS Agent")
    
    print("""
🚀 This script will help you set up WhatsApp Business API for your SMS Agent.

📋 Prerequisites:
1. Meta Business Account created
2. WhatsApp Business API app created
3. Phone number verified and approved

🔗 If you haven't done these steps yet:
   - Business Account: https://business.facebook.com/
   - Developer Console: https://developers.facebook.com/
   - WhatsApp Setup Guide: https://developers.facebook.com/docs/whatsapp/getting-started
""")
    
    if not input("\nDo you have your WhatsApp Business API credentials ready? (y/n): ").lower().startswith('y'):
        print("\n📖 Setup Guide:")
        print("1. Create Meta Business Account: https://business.facebook.com/")
        print("2. Create App in Developer Console: https://developers.facebook.com/")
        print("3. Add WhatsApp product to your app")
        print("4. Get Phone Number ID and Access Token from API Setup")
        print("5. Run this script again with your credentials")
        return
    
    print_section("WhatsApp Business API Configuration")
    
    # Get credentials
    api_url = get_user_input("WhatsApp API URL", "https://graph.facebook.com/v17.0")
    token = get_user_input("Access Token (from Meta Developer Console)", sensitive=True)
    phone_number_id = get_user_input("Phone Number ID (from WhatsApp API Setup)")
    
    if not all([api_url, token, phone_number_id]):
        print("❌ Missing required credentials. Setup cancelled.")
        return
    
    # Test credentials
    print_section("Testing Configuration")
    if not test_whatsapp_credentials(api_url, token, phone_number_id):
        if not input("Credentials test failed. Continue anyway? (y/n): ").lower().startswith('y'):
            return
    
    # Save configuration
    whatsapp_config = {
        'WHATSAPP_API_URL': api_url,
        'WHATSAPP_TOKEN': token,
        'WHATSAPP_PHONE_NUMBER_ID': phone_number_id
    }
    
    print_section("Saving Configuration")
    if update_env_file(whatsapp_config):
        print("✅ WhatsApp Business API configuration saved to .env file")
    else:
        print("❌ Failed to save configuration")
        return
    
    print_header("Setup Complete!")
    print("🎉 WhatsApp Business API is now configured!")
    
    print(f"""
📋 Configuration Summary:
   API URL: {api_url}
   Phone Number ID: {phone_number_id}
   Token: {'*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'}

📱 Next Steps:
1. Test configuration: python -c "import asyncio; from app.tools.messaging_tool import MessagingTool; asyncio.run(MessagingTool().execute({{'message_type': 'whatsapp', 'recipient': '+1234567890', 'message': 'Test from SMS Agent!'}}))"
2. Run examples: python examples/messaging_examples.py
3. Check message delivery in WhatsApp Business Manager

⚠️  Important Notes:
   - Messages can only be sent to verified phone numbers initially
   - You may need to request production access from Meta
   - Business verification may be required for higher limits
   - Test with your own phone number first

🔒 Security:
   - Keep your access token secure
   - Regularly rotate your tokens
   - Monitor API usage in Meta Business Manager
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check your credentials and try again.") 