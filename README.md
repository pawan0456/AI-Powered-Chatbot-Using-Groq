# ✦ SmartChat AI — Ultimate Edition

A stunning AI chatbot with glassmorphism dark UI, built on Groq + Tavily + Streamlit.

## ⚡ Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🔑 Setup API Keys (top of app.py)

```python
GROQ_API_KEY   = "your_groq_api_key_here"    # https://console.groq.com
TAVILY_API_KEY = "your_tavily_api_key_here"  # https://tavily.com
```

## ✨ Features

| Feature | Details |
|---|---|
| 🎨 **Glassmorphism UI** | Deep space dark theme, gradient accents, blur effects |
| 📄 **PDF Chat** | Upload any PDF and ask questions about it |
| 🖼 **Image Understanding** | Upload images — auto-routes to vision model |
| 🌐 **Web Search** | Live Tavily search for real-time answers |
| 🎭 **8 Personas** | Assistant, Tutor, Coder, Writer, Analyst, Chef, Comedian, Doctor |
| 💬 **Multi-session** | Multiple named chats, auto-titled from first message |
| 💡 **Follow-up chips** | Clickable follow-up questions after each reply |
| 👍 **Reactions** | Thumbs up/down on every message |
| 🔗 **Source citations** | Expandable web search sources |
| 📥 **Export** | Download chat as Markdown |
| ⚙️ **Custom system prompt** | Override any persona |
| 🔒 **XSS safe** | User input sanitized |
| 🔄 **Rolling window** | Last 20 messages — no context overflow |

## 🧠 Models

- LLaMA 3.3 70B (best quality)
- LLaMA 3.1 8B (fastest)  
- LLaMA 4 Scout (vision — auto-selected for images)
- LLaMA 4 Maverick
- Qwen 3 32B
- Mixtral 8x7B
