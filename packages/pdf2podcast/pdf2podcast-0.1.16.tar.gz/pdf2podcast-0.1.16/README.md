# 🎙️ PDF2Podcast

An advanced Python system for converting PDF documents into audio podcasts with natural dialogues between hosts and experts.

## ✨ Key Features

- 📄 **PDF Extraction**: Advanced PDF document processing
- 🤖 **LLM Integration**: Support for Google Gemini and other models
- 🗣️ **Multi-TTS**: Amazon Polly, Google TTS, Azure TTS, Kokoro TTS
- 💬 **Natural Dialogues**: Realistic conversations between host and expert
- 🔍 **Semantic Retrieval**: Intelligent content selection
- 🎯 **Structured Chapters**: Automatic organization into thematic chapters
- 🌍 **Multilingual**: Support for multiple languages
- 🛠️ **Modular**: Extensible and customizable architecture

## 🚀 Quick Install

```bash
pip install pdf2podcast
```

## 📖 Basic Usage

### Simple Example

```python
from pdf2podcast import PodcastGenerator
from pdf2podcast.core.rag import AdvancedPDFProcessor

# Setup
processor = AdvancedPDFProcessor()
generator = PodcastGenerator(
    rag_system=processor,
    llm_provider="gemini",
    tts_provider="google",
    llm_config={"api_key": "your-gemini-key"},
    tts_config={"language": "en"}
)

# Generate podcast
result = generator.generate(
    pdf_path="document.pdf",
    output_path="podcast.mp3",
    dialogue=True,  # Dialogue between host and expert
    query="Explain the main concepts of the document"
)

print(f"Podcast generated: {result['audio']['path']}")
print(f"Duration: {result['total_duration']:.1f} seconds")
```

### With Direct Text

```python
# From text instead of PDF
result = generator.generate(
    text="Your text content here...",
    output_path="podcast.mp3",
    dialogue=True,
    query="Discuss the key points"
)
```

## 🔧 Advanced Configuration

### Semantic Retrieval

```python
from pdf2podcast.core.processing import SimpleChunker, SemanticRetriever

chunker = SimpleChunker()
retriever = SemanticRetriever()

generator = PodcastGenerator(
    rag_system=processor,
    llm_provider="gemini",
    tts_provider="kokoro",
    chunker=chunker,
    retriever=retriever,
    k=5  # Top 5 most relevant chunks
)
```

### Custom Prompts

```python
from pdf2podcast.core.prompts import PodcastPromptBuilder

# Custom instructions
instructions = """
Focus on practical aspects and real-world applications.
Use concrete examples and accessible language.
"""

prompt_builder = PodcastPromptBuilder(
    instructions=instructions,
    dialogue=True
)

generator = PodcastGenerator(
    rag_system=processor,
    llm_provider="gemini",
    tts_provider="azure",
    llm_config={"prompt_builder": prompt_builder}
)
```

### Multi-Voice TTS (Kokoro)

```python
# Different voices for host and expert
generator = PodcastGenerator(
    rag_system=processor,
    llm_provider="gemini",
    tts_provider="kokoro",
    tts_config={
        "voice_id": ["af_heart", "am_liam"],  # [host, expert]
        "language": "en"
    }
)
```

## 🎭 Output Modes

### Dialogue (Recommended)
- **Activation**: `dialogue=True`
- **Format**: Natural conversation between S1 (host) and S2 (expert)
- **Features**: Interruptions, questions, clarifications
- **Ideal for**: Complex content, educational material

### Monologue
- **Activation**: `dialogue=False`
- **Format**: Continuous narration
- **Features**: Linear flow, storytelling
- **Ideal for**: Narrative content, summaries

## 🔌 Supported Providers

### LLM (Large Language Models)
- **Google Gemini** ✅ (Recommended)
- **OpenAI** 🔄 (In development)

### TTS (Text-to-Speech)
- **Google TTS** ✅ - Basic quality, easy setup
- **Amazon Polly** ✅ - Professional quality
- **Azure TTS** ✅ - Advanced neural voices
- **Kokoro TTS** ✅ - Local, multiple voices, precise timing

## 🛠️ Architecture

```
📦 pdf2podcast
├── 🎯 PodcastGenerator (Main orchestrator)
├── 📄 RAG Systems (Text extraction)
├── 🧠 LLM Integration (Script generation)
├── 🎵 TTS Engines (Voice synthesis)
├── 🔍 Semantic Retrieval (Intelligent search)
└── 📝 Parser System (Output validation)
```

### Processing Flow

1. **Input** → PDF/Text
2. **RAG** → Content extraction and cleaning
3. **Chunking** → Division into segments
4. **Retrieval** → Relevant content selection
5. **LLM** → Structured script generation
6. **Parsing** → Format validation
7. **TTS** → Audio conversion
8. **Output** → Audio file + metadata

## 📚 Complete Documentation

- 📖 [Module Documentation](MODULES_DOCUMENTATION.md) - Detailed architecture
- 💡 [Advanced Examples](examples/) - Use cases and configurations
- 🔧 [API Reference](docs/api.md) - Complete API documentation

## ⚙️ Environment Setup

### Environment Variables

```bash
# .env file
GENAI_API_KEY=your_gemini_api_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AZURE_SUBSCRIPTION_KEY=your_azure_key
AZURE_REGION_NAME=your_azure_region
```

### System Dependencies

```bash
# For Kokoro TTS (optional)
pip install torch torchaudio

# For advanced PDF processing
pip install pypdf2 pdfplumber
```

## 🎯 Practical Examples

### Scientific Paper Podcast

```python
result = generator.generate(
    pdf_path="research_paper.pdf",
    output_path="research_podcast.mp3",
    dialogue=True,
    query="Explain methodology, results and implications",
    instructions="Focus on practical applications and limitations"
)
```

### Technical Documentation Podcast

```python
result = generator.generate(
    pdf_path="technical_manual.pdf",
    output_path="tutorial_podcast.mp3",
    dialogue=True,
    query="Create a step-by-step tutorial",
    instructions="Use concrete examples and common troubleshooting"
)
```

### Multilingual Podcast

```python
# Italian
generator = PodcastGenerator(
    rag_system=processor,
    llm_provider="gemini",
    tts_provider="google",
    llm_config={"language": "it"},
    tts_config={"language": "it"}
)

result = generator.generate(
    text="Italian content here...",
    query="Discuss the main points in Italian"
)
```

## 🔍 Troubleshooting

### Common Issues

**1. API Key Error**
```python
# Verify configuration
import os
print("Gemini Key:", os.getenv("GENAI_API_KEY")[:10] + "..." if os.getenv("GENAI_API_KEY") else "Not found")
```

**2. Low Audio Quality**
```python
# Use premium TTS provider
tts_config = {
    "voice_id": "Joanna",  # Polly
    "engine": "neural"     # Higher quality
}
```

**3. Short Scripts**
```python
# Increase retrieval chunks
generator = PodcastGenerator(..., k=10)  # More content
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit: `git commit -am 'Add new feature'`
4. Push: `git push origin feature/new-feature`
5. Create Pull Request

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Credits

- **LangChain** - LLM Framework
- **Pydantic** - Data validation
- **Sentence Transformers** - Semantic embeddings
- **Community Contributors** - Feedback and improvements

---

## 🚀 Roadmap

- [ ] **OpenAI Integration** - GPT-4 support
- [ ] **Batch Processing** - Multiple file processing
- [ ] **Web Interface** - Web-based GUI
- [ ] **Audio Effects** - Background music, effects
- [ ] **Export Formats** - MP3, WAV, OGG
- [ ] **Cloud Deployment** - Docker, AWS Lambda

**Last updated**: December 2024
**Version**: 1.0.0
