# 🎯 InfluencerFlow AI Platform

**Next-Generation AI-Powered Influencer Marketing & Negotiation Platform**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)](https://openai.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Voice%20AI-purple)](https://elevenlabs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Transform influencer negotiations from days of back-and-forth emails into minutes of intelligent, data-driven conversations.

---

## 🚀 **Features**

### **🤖 AI-Powered Negotiation**
- **Smart Strategy Generation**: AI analyzes creator profiles and market data to suggest optimal negotiation strategies
- **Real-Time Insights**: Live ROI calculations, cost-per-view analysis, and market comparisons
- **Adaptive Responses**: Context-aware AI that adjusts strategy based on conversation flow

### **🎤 Voice-to-Voice Negotiation**
- **Speech Recognition**: Convert voice input to text using OpenAI Whisper
- **Natural Voice Responses**: Generate human-like voice responses using ElevenLabs
- **Multi-Language Support**: English, Hindi, Spanish, French, and more
- **Professional Voice Personas**: Multiple voice profiles for different negotiation styles

### **📊 Data-Driven Decision Making**
- **Creator Database**: Comprehensive profiles with performance metrics and audience demographics
- **Market Benchmarks**: Industry-standard rate comparisons across niches and platforms
- **Performance Analytics**: Engagement rates, completion rates, and collaboration scores
- **ROI Projections**: Real-time campaign performance predictions

### **💬 Intelligent Conversation Management**
- **Conversation Tracking**: Complete negotiation history with timestamps and context
- **Deal Parameter Updates**: Automatic tracking of price changes, deliverables, and terms
- **Status Management**: Progress tracking from initial contact to final agreement
- **Performance Metrics**: Negotiation success rates and time-to-closure analytics

---

## 🛠 **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend API** | FastAPI + Python | High-performance REST API |
| **Package Manager** | UV | Fast Python package installer |
| **AI Engine** | OpenAI GPT-4 | Negotiation strategy and responses |
| **Voice Processing** | OpenAI Whisper + ElevenLabs | Speech-to-text and text-to-speech |
| **Data Management** | Pydantic + JSON | Type-safe data models and storage |
| **Real-Time Processing** | Async/Await | Non-blocking voice and AI operations |
| **API Documentation** | FastAPI Auto-docs | Interactive API documentation |

### **Why UV Package Manager?**

- **⚡ Speed**: 10-100x faster than pip
- **🔒 Reliable**: Deterministic dependency resolution
- **🧹 Clean**: Better virtual environment management
- **🔄 Compatible**: Works with existing pip workflows
- **📦 Modern**: Built with Rust for performance

---

## 📦 **Installation**

### **Prerequisites**
- Python 3.8 or higher
- [uv package manager](https://github.com/astral-sh/uv) (recommended) or pip
- OpenAI API key
- ElevenLabs API key (optional, for voice features)

### **Quick Start**

#### **Method 1: Using UV (Recommended)**

1. **Install UV Package Manager**
   ```bash
   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
   # or: pip install uv
   ```

2. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/influencerflow-ai.git
   cd influencerflow-ai
   ```

3. **Create Virtual Environment**
   ```bash
   python -m venv influencer-ai
   ```

4. **Install Dependencies with UV**
   ```bash
   # Core dependencies
   uv pip install --python influencer-ai\Scripts\python.exe fastapi>=0.105.0
   uv pip install --python influencer-ai\Scripts\python.exe "uvicorn[standard]>=0.24.0"
   uv pip install --python influencer-ai\Scripts\python.exe pydantic>=2.5.0
   uv pip install --python influencer-ai\Scripts\python.exe openai>=1.6.0
   uv pip install --python influencer-ai\Scripts\python.exe elevenlabs>=0.2.26
   uv pip install --python influencer-ai\Scripts\python.exe python-decouple>=3.8
   uv pip install --python influencer-ai\Scripts\python.exe python-multipart>=0.0.6
   uv pip install --python influencer-ai\Scripts\python.exe aiofiles>=23.2.0
   uv pip install --python influencer-ai\Scripts\python.exe httpx>=0.25.2
   ```

   **Or install all at once:**
   ```bash
   uv pip install --python influencer-ai\Scripts\python.exe fastapi>=0.105.0 "uvicorn[standard]>=0.24.0" pydantic>=2.5.0 openai>=1.6.0 elevenlabs>=0.2.26 python-decouple>=3.8 python-multipart>=0.0.6 aiofiles>=23.2.0 httpx>=0.25.2
   ```

#### **Method 2: Using Traditional Pip**

1. **Clone and Create Environment**
   ```bash
   git clone https://github.com/your-username/influencerflow-ai.git
   cd influencerflow-ai
   python -m venv influencer-ai
   source influencer-ai/bin/activate  # Linux/Mac
   # or influencer-ai\Scripts\activate  # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install fastapi>=0.105.0 "uvicorn[standard]>=0.24.0" pydantic>=2.5.0 openai>=1.6.0 elevenlabs>=0.2.26 python-decouple>=3.8 python-multipart>=0.0.6 aiofiles>=23.2.0 httpx>=0.25.2
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Activate Virtual Environment** (if not already activated)
   ```bash
   # Windows
   influencer-ai\Scripts\activate
   
   # Linux/Mac
   source influencer-ai/bin/activate
   ```

6. **Start the Server**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

7. **Access the Application**
   - **API**: http://localhost:8000
   - **Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/health

### **Dependencies List**

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | ≥0.105.0 | Web framework |
| `uvicorn[standard]` | ≥0.24.0 | ASGI server |
| `pydantic` | ≥2.5.0 | Data validation |
| `openai` | ≥1.6.0 | AI integration |
| `elevenlabs` | ≥0.2.26 | Voice synthesis |
| `python-decouple` | ≥3.8 | Environment config |
| `python-multipart` | ≥0.0.6 | File uploads |
| `aiofiles` | ≥23.2.0 | Async file handling |
| `httpx` | ≥0.25.2 | HTTP client |

### **Generate Requirements File** (Optional)

If you need a traditional `requirements.txt` for compatibility:

```bash
# Generate requirements.txt from current environment
uv pip freeze --python influencer-ai\Scripts\python.exe > requirements.txt

# Or create manually
echo "fastapi>=0.105.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
openai>=1.6.0
elevenlabs>=0.2.26
python-decouple>=3.8
python-multipart>=0.0.6
aiofiles>=23.2.0
httpx>=0.25.2" > requirements.txt
```

---

## ⚙️ **Configuration**

### **Environment Variables**

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for voice features)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional (development)
DEBUG=True
LOG_LEVEL=INFO
```

### **API Keys Setup**

#### **OpenAI API Key**
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Add to your `.env` file

#### **ElevenLabs API Key** (Optional)
1. Visit [ElevenLabs](https://elevenlabs.io/)
2. Create an account
3. Go to Profile Settings → API Keys
4. Generate a new API key
5. Add to your `.env` file

---

## 🎯 **Usage Examples**

### **1. Quick API Test**

```bash
# Health check
curl http://localhost:8000/api/health

# Get all creators
curl http://localhost:8000/api/creators
```

### **2. Create Campaign Brief**

```python
import requests

campaign_data = {
    "creator_name": "TechReviewer_Sarah",
    "budget": 4000,
    "deliverables": ["video_review", "instagram_post"],
    "timeline": "2 weeks",
    "campaign_type": "product_review"
}

response = requests.post(
    "http://localhost:8000/api/campaign/brief",
    json=campaign_data
)
print(response.json())
```

### **3. Start Negotiation**

```python
negotiation_data = {
    "conversation_id": "your_conversation_id",
    "message": "Hi! We'd like to collaborate on a tech product review.",
    "speaker": "agency"
}

response = requests.post(
    "http://localhost:8000/api/negotiate",
    json=negotiation_data
)
print(response.json())
```

### **4. Voice Negotiation**

```python
# Upload audio file for voice negotiation
files = {"audio_file": open("voice_message.wav", "rb")}
response = requests.post(
    f"http://localhost:8000/api/negotiate/voice?conversation_id={conversation_id}",
    files=files
)
print(response.json())
```

---

## 📚 **API Documentation**

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/campaign/brief` | Create new campaign |
| `POST` | `/api/negotiate` | Text-based negotiation |
| `POST` | `/api/negotiate/voice` | Voice-based negotiation |
| `GET` | `/api/creators` | List all creators |
| `GET` | `/api/creators/{id}` | Get creator details |
| `GET` | `/api/conversation/{id}` | Get conversation history |
| `GET` | `/api/conversation/{id}/insights` | Get negotiation insights |

### **Interactive Documentation**

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎭 **Demo Scenarios**

### **Voice Demo Walkthrough**

1. **Start the application** and click "Demo 1"
2. **Click the microphone** and say:
   > *"Hi Sarah! We'd like to collaborate on a wireless charging pad review. Our budget is $4,000."*
3. **Listen to AI response** and continue the conversation
4. **Watch real-time updates** in the strategy panel and deal parameters

### **Sample Creators Available**

| Creator | Platform | Followers | Niche | Rate |
|---------|----------|-----------|-------|------|
| TechReviewer_Sarah | YouTube | 500K | Tech | $4,500 |
| FitnessGuru_Mike | Instagram | 300K | Fitness | $3,200 |
| BeautyInfluencer_Priya | TikTok | 1M | Beauty | $6,000 |
| GamingStreamer_Alex | Twitch | 800K | Gaming | $5,500 |
| FoodBlogger_Lisa | YouTube | 250K | Food | $2,800 |

---

## 🏗️ **Project Structure**

```
influencerflow-ai/
├── main.py                     # FastAPI application entry point
├── models/                     # Pydantic data models
│   ├── conversation.py         # Conversation and deal models
│   └── creator.py             # Creator profile models
├── services/                   # Business logic services
│   ├── negotiation.py         # Main negotiation orchestration
│   ├── openai_service.py      # OpenAI integration
│   ├── voice_service.py       # Voice processing
│   ├── data_service.py        # Data management
│   └── conversation_manager.py # Conversation state management
├── data/                       # Static data files
│   ├── creators.json          # Creator database
│   └── market_data.json       # Market benchmarks
├── influencer-ai/              # Virtual environment (ignored by git)
├── .env.example               # Environment variables template
├── .env                       # Environment variables (ignored by git)
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

---

## 🔧 **Development**

### **Running in Development Mode**

```bash
# Start with auto-reload
uvicorn main:app --reload --port 8000

# Start with specific log level
uvicorn main:app --reload --port 8000 --log-level debug
```

### **Adding New Creators**

Edit `data/creators.json`:

```json
{
  "id": "new_creator_id",
  "name": "CreatorName",
  "platform": "YouTube",
  "followers": 100000,
  "niche": "lifestyle",
  "typical_rate": 2500,
  "engagement_rate": 3.5,
  // ... other required fields
}
```

### **Customizing Voice Profiles**

Edit `services/voice_service.py`:

```python
self.voice_profiles = {
    "custom_voice": {
        "voice_id": "your_elevenlabs_voice_id",
        "settings": {
            "stability": 0.75,
            "similarity_boost": 0.85,
            "style": 0.15,
            "use_speaker_boost": True
        }
    }
}
```

---

## 🧪 **Testing**

### **Manual Testing**

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test creator endpoint
curl http://localhost:8000/api/creators

# Test market data
curl http://localhost:8000/api/market-data
```

### **Testing Voice Features**

1. Ensure microphone permissions are enabled
2. Use Chrome or Firefox for best compatibility
3. Speak clearly for better transcription accuracy
4. Check browser console for any errors

---

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### **Development Guidelines**

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for public methods
- Update tests for new features
- Update documentation as needed

---

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **OpenAI** for GPT-4 and Whisper APIs
- **ElevenLabs** for voice synthesis technology
- **FastAPI** for the excellent web framework
- **Pydantic** for data validation and serialization

---

## 📞 **Support**

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-username/influencerflow-ai/issues)
- **Email**: support@influencerflow.ai

---

## 🚀 **What's Next?**

- [ ] Frontend React application
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real-time WebSocket connections
- [ ] Advanced analytics dashboard
- [ ] Multi-language conversation support
- [ ] Integration with social media APIs
- [ ] Campaign performance tracking
- [ ] Advanced AI training on negotiation data

---

**Built with ❤️ for the future of influencer marketing**