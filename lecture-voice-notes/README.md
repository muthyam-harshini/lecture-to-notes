# 🎓 Lecture Voice Notes

Transform your audio lectures into comprehensive study materials using AI! This application converts audio recordings into transcripts, summaries, quizzes, and flashcards automatically.

## ✨ Features

- 🎤 **Speech-to-Text**: Convert audio lectures to text using OpenAI Whisper
- 📝 **Smart Summaries**: Generate comprehensive summaries with key concepts
- ❓ **Auto Quiz Generation**: Create multiple choice, true/false, and short answer questions
- 📚 **Flashcard Creation**: Generate study flashcards in multiple formats
- 💾 **Data Persistence**: Save and manage your lecture library
- 🔍 **Search & Browse**: Find specific lectures and content
- 📥 **Export Options**: Download content in various formats including Anki-compatible files

## 📁 Project Structure

```
lecture-voice-notes/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env                        # API keys (you need to create this)
│
├── audio/                      # Uploaded audio files storage
│
├── database/
│   └── database.py             # SQLite database management
│
├── models/
│   ├── speech_to_text.py       # Whisper integration
│   ├── summarizer.py           # Text summarization
│   ├── quiz_generator.py       # Quiz creation
│   └── flashcard_generator.py  # Flashcard generation
│
├── utils/
│   └── text_processing.py      # Text cleaning and processing
│
└── data/
    └── lecture_notes.db        # SQLite database (auto-created)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git (optional)

### Installation

1. **Clone or Download the Project**
   ```bash
   # Option 1: Clone with Git
   git clone <repository-url>
   cd lecture-voice-notes
   
   # Option 2: Download and extract the ZIP file
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\\Scripts\\activate
   
   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   **Get your OpenAI API key:**
   - Go to https://platform.openai.com/account/api-keys
   - Create a new secret key
   - Copy and paste it into your `.env` file

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

6. **Open in Browser**
   The app will open automatically at `http://localhost:8501`

## 🎯 How to Use

### 1. Upload Audio File

- Click "Upload Audio Lecture" on the main page
- Select your audio file (supports MP3, WAV, M4A, FLAC, OGG, MP4, AVI, MOV)
- Choose processing options

### 2. Configure Processing

- **Model Size**: Choose Whisper model (larger = more accurate but slower)
  - `tiny`: Fastest, basic accuracy
  - `base`: Good balance (recommended)
  - `small`: Better accuracy
  - `medium`: High accuracy
  - `large`: Best accuracy, slowest

- **Language**: Auto-detect or specify (e.g., 'en', 'es', 'fr')

- **Content Generation**: Select what to generate
  - ✅ Summary (with key concepts and learning objectives)
  - ✅ Quiz (multiple choice, true/false, short answer)
  - ✅ Flashcards (concepts, definitions, applications)

### 3. View Results

- **Summary Tab**: Comprehensive summary with key concepts
- **Quiz Tab**: Generated questions with answers
- **Flashcards Tab**: Study cards in multiple formats

### 4. Download & Export

- Download summaries as text files
- Export quizzes as Markdown
- Get flashcards in Anki-compatible format

### 5. Manage Library

- Use "View Saved Lectures" to browse your collection
- Search through transcripts and content
- Delete old lectures as needed

## 🔧 Advanced Configuration

### Model Sizes Comparison

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | ~39 MB | Fastest | Basic | Quick drafts |
| base | ~74 MB | Fast | Good | General use |
| small | ~244 MB | Moderate | Better | Important content |
| medium | ~769 MB | Slow | High | Academic lectures |
| large | ~1550 MB | Slowest | Best | Critical transcription |

### Audio Format Support

**Recommended formats:**
- MP3 (most compatible)
- WAV (highest quality)
- M4A (good for mobile recordings)

**Also supported:**
- FLAC, OGG, MP4, AVI, MOV

### API Usage and Costs

This app uses OpenAI's API which charges based on usage:
- **Whisper**: ~$0.006 per minute of audio
- **GPT-3.5-turbo**: ~$0.001 per 1K tokens
- **Typical cost per 1-hour lecture**: $0.36-0.60

Monitor your usage at https://platform.openai.com/usage

## 🛠️ Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Ensure `.env` file exists in project root
- Check that the key starts with `sk-`
- Verify no extra spaces in the `.env` file

**Audio processing fails**
- Try converting to MP3 or WAV format
- Check file isn't corrupted
- Ensure file size is reasonable (<100MB recommended)

**Slow processing**
- Use smaller Whisper model (tiny/base)
- Process shorter audio segments
- Ensure stable internet connection

**Memory issues**
- Close other applications
- Use smaller model sizes
- Process files individually rather than batch

### Performance Optimization

1. **For speed**: Use `tiny` or `base` Whisper models
2. **For accuracy**: Use `small` or `medium` models  
3. **For long lectures**: Split into smaller segments
4. **For batch processing**: Use the batch processing page

## 📚 Project Components

### Core Models

- **SpeechToText**: Handles audio transcription using Whisper
- **TextSummarizer**: Creates summaries and extracts key concepts
- **QuizGenerator**: Generates various types of quiz questions
- **FlashcardGenerator**: Creates study flashcards
- **TextProcessor**: Cleans and processes transcripts

### Database

- SQLite database for storing lecture data
- Automatic schema creation
- Full CRUD operations for lectures

### Web Interface

- Streamlit-based web application
- Responsive design with tabs and expandable sections
- File upload with format validation
- Progress indicators and error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙋‍♀️ Support

For issues and questions:

1. Check this README and troubleshooting section
2. Review error messages carefully
3. Verify API key configuration
4. Test with smaller audio files first

## 🔄 Updates

### Version 1.0.0
- Initial release
- Basic transcription and content generation
- Web interface
- Database storage

### Planned Features
- Multiple language support
- Advanced text analysis
- Export to more formats
- Collaborative features
- Mobile app

---

**Made with ❤️ using OpenAI Whisper, GPT-3.5, and Streamlit**