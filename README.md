# 🧠 MeetMind AI

<p align="center">
  <h3 align="center">AI-Powered Meeting Intelligence Assistant</h3>
  <p align="center">
    Transcribe • Summarize • Extract Insights • Chat with Meetings
  </p>
</p>

---

## 📖 Overview

**MeetMind AI** is an intelligent meeting assistant that transforms meeting recordings into structured, actionable insights using Generative AI.

Users can upload a **YouTube video** or a **local audio/video file**, and MeetMind AI automatically:

- 🎙️ Converts speech into text
- 📝 Generates concise meeting summaries
- 🏷️ Creates AI-generated meeting titles
- ✅ Extracts action items
- 🔑 Identifies key decisions
- ❓ Detects unanswered questions
- 💬 Allows users to chat with the meeting transcript using Retrieval-Augmented Generation (RAG)

The project is built with **Python**, **Streamlit**, **OpenAI**, **Whisper**, **LangChain**, and **ChromaDB**.

---

# ✨ Features

- 🎥 Supports YouTube videos and local media files
- 🎙️ Speech-to-Text transcription using Whisper
- 📝 AI-generated meeting summaries
- 🏷️ Automatic meeting title generation
- ✅ Action Item Extraction
- 🔑 Key Decision Detection
- ❓ Open Question Extraction
- 💬 Chat with Meeting using RAG
- 📥 Download transcript
- 📥 Download complete meeting report
- 🌙 Modern Streamlit Dashboard
- 📊 Live pipeline progress tracking

---

# 🛠 Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python |
| Frontend | Streamlit |
| Speech Recognition | OpenAI Whisper |
| LLM | OpenAI |
| Framework | LangChain |
| Vector Database | ChromaDB |
| Video Download | yt-dlp |
| Audio Processing | FFmpeg |
| Environment | python-dotenv |

---

# 📂 Project Structure

```text
MeetMind-AI/
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── downloads/
│
├── vector_db/
│
├── app.py
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/MeetMind-AI.git
```

Go into the project directory

```bash
cd MeetMind-AI
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_openai_api_key
```

If your project uses additional API keys, add them here as well.

---

# ▶️ Running the Application

Launch the Streamlit app:

```bash
streamlit run app.py
```

Open your browser:

```
http://localhost:8501
```

---

# 🏗 System Workflow

```text
                 User Input
        (YouTube URL / Local File)
                     │
                     ▼
          Audio Extraction & Chunking
                     │
                     ▼
           Whisper Speech Transcription
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
 Meeting Title   AI Summary   Information Extraction
                                    │
                    ┌───────────────┼──────────────┐
                    ▼               ▼              ▼
              Action Items    Key Decisions   Open Questions
                                    │
                                    ▼
                          Chroma Vector Database
                                    │
                                    ▼
                           Retrieval-Augmented
                           Question Answering
                                    │
                                    ▼
                        Interactive Streamlit UI
```

---

# 📋 Example Output

## 📝 Meeting Summary

- Discussed project progress
- Assigned frontend development tasks
- Planned deployment timeline

---

## ✅ Action Items

- Complete frontend implementation
- Deploy application
- Prepare project documentation

---

## 🔑 Key Decisions

- Use Whisper for transcription
- Implement LangChain for RAG
- Build the frontend using Streamlit

---

## ❓ Open Questions

- Which deployment platform should be used?
- Should multi-language support be added?

---


# 🚀 Future Enhancements

- 🌍 Multi-language transcription
- 🎙 Speaker diarization
- 📄 PDF report generation
- 📧 Email meeting summaries
- 📅 Google Calendar integration
- ☁️ Cloud deployment
- 🔒 User authentication
- 📊 Meeting analytics dashboard
- ⚡ Faster inference with GPU support

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Added new feature"
```

4. Push your branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 👩‍💻 Author

**Your Name**

GitHub: https://github.com/yourusername

LinkedIn: https://linkedin.com/in/yourprofile

---

# 📜 License

This project is intended for educational and portfolio purposes.

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!

It helps others discover the project and motivates future improvements.
