# 📞 Enable Real ElevenLabs Phone Calls

Your system is currently using **simulation mode** because ElevenLabs credentials are not configured. Here's how to enable **real phone calls**:

## 🔧 Step 1: Get ElevenLabs Credentials

1. **Sign up** at [ElevenLabs](https://elevenlabs.io/)
2. **Get your API key** from the dashboard
3. **Create an agent** for influencer negotiations
4. **Get a phone number** for outbound calls

## 🔑 Step 2: Set Environment Variables

Create a `.env` file in your project root:

```bash
# ElevenLabs Configuration for REAL calls
ELEVENLABS_API_KEY=your_actual_api_key_here
ELEVENLABS_AGENT_ID=your_agent_id_here
ELEVENLABS_PHONE_NUMBER_ID=your_phone_number_id_here

# Required for AI strategy generation
GROQ_API_KEY=your_groq_api_key_here

# Optional - Demo settings
DEMO_MODE=false
MOCK_CALLS=false
```

## 📋 Step 3: Test Real Call Setup

Test if your credentials work:

```bash
curl -X GET "http://localhost:8000/api/webhook/test-enhanced-elevenlabs"
```

**Expected response for real calls:**
```json
{
  "status": "success",
  "message": "Enhanced ElevenLabs integration ready",
  "api_connected": true
}
```

**Current response (simulation):**
```json
{
  "status": "success", 
  "api_connected": false
}
```

## 🎯 Step 4: Test Real Campaign

Use this JSON in SwaggerUI to trigger real calls:

```json
{
  "campaign_id": "real_call_test_001",
  "product_name": "Real Call Test Product",
  "brand_name": "Test Brand",
  "product_description": "Testing real ElevenLabs calls",
  "target_audience": "test audience",
  "campaign_goal": "test real calling functionality",
  "product_niche": "tech",
  "total_budget": 5000
}
```

## 📊 What Changes With Real Calls

### **Before (Simulation):**
```
INFO:agents.enhanced_orchestrator:📞 Processing creator 1: TechReviewer_Sarah 
INFO:agents.enhanced_orchestrator:✅ Successful negotiation: TechReviewer_Sarah - $5400.0
```
*Instant completion (simulation)*

### **After (Real Calls):**
```
INFO:agents.enhanced_orchestrator:📞 Initiating REAL call to TechReviewer_Sarah at +918806859890
INFO:agents.enhanced_orchestrator:📞 Call started successfully: conv_123456
INFO:agents.enhanced_orchestrator:📞 Waiting for call completion...
INFO:agents.enhanced_orchestrator:✅ Call completed - SUCCESS: $4800.0
```
*Takes 2-5 minutes (real conversation)*

## ⚠️ Important Notes

1. **Real calls cost money** - ElevenLabs charges per call
2. **Phone numbers must be valid** - Invalid numbers will fail
3. **Calls take time** - 2-5 minutes per influencer
4. **Rate limits apply** - Don't exceed ElevenLabs API limits

## 🔍 Debugging Real Calls

Check logs for these patterns:

**✅ Good (Real calls enabled):**
```
INFO:services.enhanced_voice:✅ ElevenLabs service initialized with real API
INFO:agents.enhanced_orchestrator:📞 Initiating REAL call to...
```

**⚠️ Still using simulation:**
```
INFO:services.enhanced_voice:⚠️ ElevenLabs credentials incomplete - using mock calls
WARNING:agents.enhanced_orchestrator:⚠️ Using fallback simulation instead of real calls
```

## 🚀 Quick Test

After setting up credentials, restart your server and test:

```bash
# 1. Restart server
uv run uvicorn main:app --reload

# 2. Test credentials
curl "http://localhost:8000/api/webhook/test-enhanced-elevenlabs"

# 3. Run campaign and watch logs for "REAL call" messages
```

Your system will automatically switch from simulation to real calls once credentials are properly configured! 📞 