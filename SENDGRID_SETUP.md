# 📧 SendGrid Email Service Setup Guide

This guide will help you set up SendGrid for automatic contract email delivery in your InfluencerFlow AI platform.

## 🚀 Quick Setup Steps

### 1. Create a SendGrid Account
1. Go to [SendGrid.com](https://sendgrid.com)
2. Sign up for a free account (100 emails/day free tier)
3. Verify your email address

### 2. Get Your API Key
1. Log into your SendGrid dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Choose **Restricted Access** and give it these permissions:
   - **Mail Send**: Full Access
5. Copy the API key (you won't see it again!)

### 3. Verify Your Sender Email
1. Go to **Settings** → **Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in your details (use a real email you can access)
4. Check your email and click the verification link

### 4. Update Your Environment Variables
Add these to your `.env` file:

```bash
# SendGrid Email Configuration
SENDGRID_API_KEY=SG.your_actual_api_key_here
SENDGRID_FROM_EMAIL=your_verified_email@yourdomain.com
SENDGRID_FROM_NAME=InfluencerFlow AI
```

**Important**: 
- Replace `your_actual_api_key_here` with your real SendGrid API key
- Replace `your_verified_email@yourdomain.com` with the email you verified in step 3
- The `FROM_EMAIL` must match exactly what you verified in SendGrid

### 5. Test Your Setup
Run the test script to make sure everything works:

```bash
# Update the test email in the script first
python test_email_service.py
```

## 🔧 Configuration Options

### Email Settings in `config/settings.py`
```python
# SendGrid Email Configuration
sendgrid_api_key: Optional[str] = None          # Your API key
sendgrid_from_email: str = "noreply@yourcompany.com"  # Verified sender email
sendgrid_from_name: str = "InfluencerFlow AI"   # Display name
```

## 📋 How It Works

### Automatic Contract Delivery
When a call is successful, the system will:

1. **Generate Contract**: Create a personalized contract with negotiated terms
2. **Send Email**: Automatically send via SendGrid with:
   - Professional HTML email template
   - Contract details in the email body
   - Optional contract attachment
   - Clear next steps for the influencer

### Email Templates
The system includes:
- **HTML Template**: Beautiful, responsive email design
- **Plain Text**: Fallback for email clients that don't support HTML
- **Professional Styling**: Branded with your company colors

## 🧪 Testing

### Test Script Features
The `test_email_service.py` script tests:
1. **Basic Email**: Simple notification email
2. **Contract Email**: Full contract with HTML template
3. **Service Integration**: Complete workflow test

### Before Testing
1. Update the `test_email` variable in `test_email_service.py`
2. Use your own email address to see the results
3. Make sure your SendGrid API key is in your `.env` file

## 🚨 Troubleshooting

### Common Issues

**"Extra inputs are not permitted" Error**
- Make sure your `.env` file has the correct variable names
- Check that `config/settings.py` includes the SendGrid fields

**"Authentication failed" Error**
- Verify your API key is correct
- Make sure the API key has "Mail Send" permissions

**"From email not verified" Error**
- Go to SendGrid dashboard → Sender Authentication
- Verify the email address you're using as `SENDGRID_FROM_EMAIL`

**Emails not being received**
- Check your spam folder
- Verify the recipient email address
- Check SendGrid dashboard for delivery logs

### Mock Mode
If you don't have SendGrid set up yet, the system will run in "mock mode":
- Logs what emails would be sent
- Doesn't actually send emails
- Useful for development and testing

## 📊 Monitoring

### SendGrid Dashboard
Monitor your email delivery:
1. Go to **Activity** in your SendGrid dashboard
2. View delivery statistics
3. Check for bounces or spam reports
4. Monitor your sending reputation

### Application Logs
The system logs all email activities:
- ✅ Successful sends
- ❌ Failed attempts
- 📧 Mock mode operations

## 🔒 Security Best Practices

1. **Keep API Keys Secret**: Never commit API keys to version control
2. **Use Environment Variables**: Store sensitive data in `.env` files
3. **Restrict API Permissions**: Only give necessary permissions to API keys
4. **Monitor Usage**: Keep an eye on your SendGrid usage and billing

## 📈 Scaling Up

### Free Tier Limits
- 100 emails/day
- Perfect for testing and small campaigns

### Paid Plans
- Higher sending limits
- Advanced features like dedicated IPs
- Better deliverability for high-volume sending

## 🎯 Next Steps

After setup:
1. Test with the provided script
2. Run a real campaign to see automatic contract delivery
3. Customize email templates if needed
4. Monitor delivery rates and optimize

---

**Need Help?** 
- Check the SendGrid documentation
- Review the application logs
- Test with the provided script
- Ensure all environment variables are set correctly 