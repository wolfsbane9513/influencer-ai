# 🎯 InfluencerFlow AI Platform

**Next-Generation AI-Powered Influencer Marketing & Negotiation Platform**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)](https://openai.com/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Voice%20AI-purple)](https://elevenlabs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Transform influencer negotiations from days of back-and-forth emails into minutes of intelligent, data-driven voice conversations.

---

## 🚀 **Features**

- **🤖 AI-Powered Negotiation**: Smart strategy generation with real-time market data
- **🎤 Voice-to-Voice Conversations**: Natural speech recognition and AI voice responses
- **📊 Data-Driven Insights**: Live ROI calculations and performance metrics
- **💬 Intelligent Context**: Conversation tracking with deal parameter updates
- **⚡ Zero Build Time**: Simple HTML + CDN setup, no npm required

---

## 🛠 **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend API** | FastAPI + Python | REST API (Port 8000) |
| **Frontend** | React 18 (CDN) + HTML | Voice interface (Port 3000) |
| **Package Manager** | UV | Fast Python dependencies |
| **AI Engine** | OpenAI GPT-4 | Negotiation intelligence |
| **Voice Processing** | Whisper + ElevenLabs | Speech ↔ text ↔ speech |
| **Styling** | Tailwind CSS (CDN) | UI components |

---

## 📦 **Installation**

### **Prerequisites**
- Python 3.8+
- [UV package manager](https://github.com/astral-sh/uv) (recommended)
- OpenAI API key
- ElevenLabs API key (optional, for voice responses)

### **Quick Setup**

1. **Clone & Setup Environment**
   ```bash
   git clone https://github.com/your-username/influencerflow-ai.git
   cd influencerflow-ai
   python -m venv influencer-ai
   
   # Windows:
   influencer-ai\Scripts\activate
   # Linux/Mac:
   source influencer-ai/bin/activate
   ```

2. **Install Dependencies with UV**
   ```bash
   uv pip install --python influencer-ai\Scripts\python.exe fastapi>=0.105.0 "uvicorn[standard]>=0.24.0" pydantic>=2.5.0 openai>=1.6.0 elevenlabs>=0.2.26 python-decouple>=3.8 python-multipart>=0.0.6 aiofiles>=23.2.0 httpx>=0.25.2
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start Both Servers**
   ```bash
   # Terminal 1: Backend
   uvicorn main:app --reload --port 8000
   
   # Terminal 2: Frontend
   python -m http.server 3000
   ```

5. **Access Application**
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://localhost:8000/docs

---

## ⚙️ **Configuration**

Create `.env` file:
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for voice features)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

---

## 🎭 **Demo Walkthrough**

### **Voice Demo Steps**

1. **Start both servers** (backend on 8000, frontend on 3000)
2. **Open** http://localhost:3000 in Chrome/Firefox
3. **Click "Demo 1"** to load TechReviewer_Sarah scenario
4. **Click microphone** and say:
   > *"Hi Sarah! We'd like to collaborate on a wireless charging pad review. Our budget is $4,000."*
5. **Listen to AI response** and continue the conversation
6. **Watch real-time updates** in deal parameters and insights panels

### **Sample Creators**

| Creator | Platform | Followers | Niche | Rate |
|---------|----------|-----------|-------|------|
| TechReviewer_Sarah | YouTube | 500K | Tech | $4,500 |
| FitnessGuru_Mike | Instagram | 300K | Fitness | $3,200 |
| BeautyInfluencer_Priya | TikTok | 1M | Beauty | $6,000 |
| GamingStreamer_Alex | Twitch | 800K | Gaming | $5,500 |
| FoodBlogger_Lisa | YouTube | 250K | Food | $2,800 |

---

## 📚 **API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/campaign/brief` | Create new campaign |
| `POST` | `/api/negotiate` | Text-based negotiation |
| `POST` | `/api/negotiate/voice` | Voice-based negotiation |
| `GET` | `/api/creators` | List all creators |
| `GET` | `/api/conversation/{id}` | Get conversation history |
| `GET` | `/api/conversation/{id}/insights` | Get negotiation insights |

**Interactive Docs**: http://localhost:8000/docs

---

## 🏗️ **Project Structure**

```
influencerflow-ai/
├── main.py                     # FastAPI application
├── index.html                  # React frontend (CDN-based)
├── models/                     # Data models
├── services/                   # Business logic
├── data/                       # Creator & market data
├── influencer-ai/              # Virtual environment
├── .env                       # Environment variables
└── README.md                  # This file
```

---

## 🔧 **Development**

### **Frontend Development**
- Edit `index.html` → refresh browser
- All React code in `<script type="text/babel">` tags
- No build process required

### **Backend Development**
- Edit Python files → FastAPI auto-reloads
- Test endpoints at http://localhost:8000/docs

### **Adding New Creators**
Edit `data/creators.json`:
```json
{
  "id": "new_creator",
  "name": "CreatorName",
  "platform": "YouTube",
  "followers": 100000,
  "niche": "lifestyle",
  "typical_rate": 2500,
  "engagement_rate": 3.5
}
```

---

## 🧪 **Testing**

### **Quick API Test**
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/creators
```

### **Voice Testing Checklist**
- [ ] Backend running on port 8000
- [ ] Frontend served via HTTP (not file://)
- [ ] Microphone permissions enabled
- [ ] OpenAI API key configured
- [ ] Using Chrome or Firefox

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📝 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **OpenAI** for GPT-4 and Whisper APIs
- **ElevenLabs** for voice synthesis
- **FastAPI** for the web framework

---

**Built with ❤️ for the future of influencer marketing**