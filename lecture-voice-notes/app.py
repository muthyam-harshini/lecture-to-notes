"""
Lecture Voice Notes - Main Streamlit Application
Transform audio lectures into summaries, quizzes, and flashcards using AI.
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Import our custom modules
from database.database import get_database
from models.speech_to_text import SpeechToText, validate_audio_file, get_supported_audio_formats
from models.summarizer import TextSummarizer, get_summary_types
from models.quiz_generator import QuizGenerator, get_quiz_types
from models.flashcard_generator import FlashcardGenerator, get_flashcard_types
from utils.text_processing import TextProcessor, preprocess_audio_transcript, get_text_insights


# Page configuration
st.set_page_config(
    page_title="Lecture Voice Notes",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
    .info-box {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class LectureVoiceNotesApp:
    def __init__(self):
        """Initialize the application."""
        self.db = get_database()
        self.text_processor = TextProcessor()
        
        # Initialize models only when needed (lazy loading)
        self._speech_to_text = None
        self._summarizer = None
        self._quiz_generator = None
        self._flashcard_generator = None
    
    @property
    def speech_to_text(self):
        """Lazy load speech to text model."""
        if self._speech_to_text is None:
            self._speech_to_text = SpeechToText()
        return self._speech_to_text
    
    @property
    def summarizer(self):
        """Lazy load summarizer model."""
        if self._summarizer is None:
            self._summarizer = TextSummarizer()
        return self._summarizer
    
    @property
    def quiz_generator(self):
        """Lazy load quiz generator model."""
        if self._quiz_generator is None:
            self._quiz_generator = QuizGenerator()
        return self._quiz_generator
    
    @property
    def flashcard_generator(self):
        """Lazy load flashcard generator model."""
        if self._flashcard_generator is None:
            self._flashcard_generator = FlashcardGenerator()
        return self._flashcard_generator
    
    def main(self):
        """Main application function."""
        st.markdown('<h1 class="main-header">🎓 Lecture Voice Notes</h1>', unsafe_allow_html=True)
        st.markdown("**Transform your audio lectures into summaries, quizzes, and flashcards using AI**")
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a page:",
            ["Upload & Process", "View Saved Lectures", "Batch Process", "Settings"]
        )
        
        # Route to appropriate page
        if page == "Upload & Process":
            self.upload_and_process_page()
        elif page == "View Saved Lectures":
            self.view_saved_lectures_page()
        elif page == "Batch Process":
            self.batch_process_page()
        elif page == "Settings":
            self.settings_page()
    
    def upload_and_process_page(self):
        """Page for uploading and processing audio files."""
        st.header("📁 Upload Audio Lecture")
        
        # File upload section
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=[fmt.lstrip('.') for fmt in get_supported_audio_formats()],
            help=f"Supported formats: {', '.join(get_supported_audio_formats())}"
        )
        
        if uploaded_file is not None:
            if validate_audio_file(uploaded_file):
                self._process_uploaded_file(uploaded_file)
            else:
                st.error("❌ Unsupported file format. Please upload a valid audio file.")
    
    def _process_uploaded_file(self, uploaded_file):
        """Process the uploaded audio file."""
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Display file info
        with st.expander("📊 File Information"):
            file_size = len(uploaded_file.read()) / (1024 * 1024)  # MB
            uploaded_file.seek(0)  # Reset file pointer
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**File size:** {file_size:.2f} MB")
            with col2:
                st.write(f"**File type:** {uploaded_file.type}")
        
        # Processing options
        st.subheader("🛠️ Processing Options")
        
        col1, col2 = st.columns(2)
        with col1:
            # Whisper model selection
            model_size = st.selectbox(
                "Speech-to-text model:",
                ["tiny", "base", "small", "medium", "large"],
                index=1,
                help="Larger models are more accurate but slower"
            )
            
            # Language detection
            auto_detect_lang = st.checkbox("Auto-detect language", value=True)
            language = None
            if not auto_detect_lang:
                language = st.text_input("Language code (e.g., 'en', 'es', 'fr')")
        
        with col2:
            # Content generation options
            st.write("**Generate:**")
            generate_summary = st.checkbox("📝 Summary", value=True)
            generate_quiz = st.checkbox("❓ Quiz", value=True)
            generate_flashcards = st.checkbox("📚 Flashcards", value=True)
        
        # Process button
        if st.button("🚀 Process Audio", type="primary"):
            self._execute_processing(uploaded_file, model_size, language, 
                                   generate_summary, generate_quiz, generate_flashcards)
    
    def _execute_processing(self, uploaded_file, model_size: str, language: Optional[str],
                           generate_summary: bool, generate_quiz: bool, generate_flashcards: bool):
        """Execute the complete processing pipeline."""
        
        # Initialize database record
        lecture_id = self.db.insert_lecture(filename=uploaded_file.name)
        
        try:
            # Step 1: Speech to Text
            st.subheader("🎤 Step 1: Transcribing Audio")
            
            # Update model if different from current
            if not hasattr(self, '_speech_to_text') or self._speech_to_text is None or self._speech_to_text.model_size != model_size:
                self._speech_to_text = SpeechToText(model_size)
            
            with st.spinner("Transcribing audio... This may take a few minutes."):
                transcription_result = self.speech_to_text.transcribe_audio(uploaded_file, language)
            
            raw_transcript = transcription_result['text']
            st.success("✅ Transcription completed!")
            
            # Display transcription info
            with st.expander("📄 Transcription Details"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Duration", f"{transcription_result['duration']:.1f}s")
                with col2:
                    st.metric("Language", transcription_result['language'])
                with col3:
                    st.metric("Word Count", len(raw_transcript.split()))
            
            # Step 2: Clean and Process Text
            st.subheader("🧹 Step 2: Processing Text")
            with st.spinner("Cleaning and processing transcript..."):
                cleaned_transcript = preprocess_audio_transcript(raw_transcript)
                text_insights = get_text_insights(cleaned_transcript)
            
            st.success("✅ Text processing completed!")
            
            # Update database with transcript
            self.db.update_lecture(lecture_id, transcript=cleaned_transcript)
            
            # Display processed transcript
            with st.expander("📝 Processed Transcript"):
                st.text_area("Cleaned Transcript", cleaned_transcript, height=200)
                
                # Text insights
                col1, col2, col3, col4 = st.columns(4)
                stats = text_insights['stats']
                with col1:
                    st.metric("Words", stats['word_count'])
                with col2:
                    st.metric("Sentences", stats['sentence_count'])
                with col3:
                    st.metric("Reading Time", f"{stats['estimated_reading_time_minutes']:.1f}m")
                with col4:
                    st.metric("Speaking Time", f"{stats['estimated_speaking_time_minutes']:.1f}m")
                
                # Keywords and topics
                st.write("**Keywords:**", ", ".join(text_insights['keywords'][:10]))
                st.write("**Topics:**", ", ".join(text_insights['topics']))
            
            # Step 3: Generate Content
            results = self._generate_content(cleaned_transcript, generate_summary, 
                                           generate_quiz, generate_flashcards)
            
            # Update database with results
            self.db.update_lecture(
                lecture_id,
                summary=results.get('summary', ''),
                quiz=json.dumps(results.get('quiz', {})),
                flashcards=json.dumps(results.get('flashcards', {}))
            )
            
            # Step 4: Display Results
            self._display_results(results, lecture_id)
            
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            # Clean up database record if processing failed
            self.db.delete_lecture(lecture_id)
    
    def _generate_content(self, transcript: str, generate_summary: bool, 
                         generate_quiz: bool, generate_flashcards: bool) -> Dict[str, Any]:
        """Generate summary, quiz, and flashcards from transcript."""
        results = {}
        
        # Generate Summary
        if generate_summary:
            st.subheader("📄 Step 3a: Generating Summary")
            
            summary_type = st.selectbox(
                "Summary type:",
                list(get_summary_types().keys()),
                format_func=lambda x: get_summary_types()[x]
            )
            
            with st.spinner("Generating summary..."):
                summary = self.summarizer.generate_summary(transcript, summary_type)
                key_concepts = self.summarizer.generate_key_concepts(transcript)
                learning_objectives = self.summarizer.generate_learning_objectives(transcript)
            
            results['summary'] = {
                'text': summary,
                'type': summary_type,
                'key_concepts': key_concepts,
                'learning_objectives': learning_objectives
            }
            
            st.success("✅ Summary generated!")
        
        # Generate Quiz
        if generate_quiz:
            st.subheader("❓ Step 3b: Generating Quiz")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                mc_questions = st.number_input("Multiple choice questions", 1, 10, 3)
            with col2:
                tf_questions = st.number_input("True/false questions", 1, 10, 2)
            with col3:
                sa_questions = st.number_input("Short answer questions", 1, 5, 2)
            
            with st.spinner("Generating quiz..."):
                quiz = self.quiz_generator.generate_comprehensive_quiz(
                    transcript, mc_questions, tf_questions, sa_questions
                )
            
            results['quiz'] = quiz
            st.success("✅ Quiz generated!")
        
        # Generate Flashcards
        if generate_flashcards:
            st.subheader("📚 Step 3c: Generating Flashcards")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                concept_cards = st.number_input("Concept cards", 1, 15, 6)
            with col2:
                definition_cards = st.number_input("Definition cards", 1, 10, 4)
            with col3:
                application_cards = st.number_input("Application cards", 1, 8, 3)
            
            with st.spinner("Generating flashcards..."):
                flashcards = self.flashcard_generator.generate_comprehensive_flashcard_set(
                    transcript, concept_cards, definition_cards, application_cards
                )
            
            results['flashcards'] = flashcards
            st.success("✅ Flashcards generated!")
        
        return results
    
    def _display_results(self, results: Dict[str, Any], lecture_id: int):
        """Display the generated content."""
        st.header("🎉 Results")
        
        # Create tabs for different content types
        tabs = []
        if 'summary' in results:
            tabs.append("📄 Summary")
        if 'quiz' in results:
            tabs.append("❓ Quiz")
        if 'flashcards' in results:
            tabs.append("📚 Flashcards")
        
        if tabs:
            selected_tabs = st.tabs(tabs)
            
            tab_index = 0
            
            # Summary Tab
            if 'summary' in results:
                with selected_tabs[tab_index]:
                    summary_data = results['summary']
                    
                    st.subheader("Summary")
                    st.write(summary_data['text'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if summary_data.get('key_concepts'):
                            st.subheader("Key Concepts")
                            for concept in summary_data['key_concepts']:
                                st.write(f"• {concept}")
                    
                    with col2:
                        if summary_data.get('learning_objectives'):
                            st.subheader("Learning Objectives")
                            for objective in summary_data['learning_objectives']:
                                st.write(f"• {objective}")
                    
                    # Download button
                    summary_text = self._format_summary_for_download(summary_data)
                    st.download_button(
                        "📥 Download Summary",
                        summary_text,
                        f"summary_lecture_{lecture_id}.txt",
                        "text/plain"
                    )
                
                tab_index += 1
            
            # Quiz Tab
            if 'quiz' in results:
                with selected_tabs[tab_index]:
                    st.subheader("Generated Quiz")
                    
                    quiz_data = results['quiz']
                    formatted_quiz = self.quiz_generator.format_quiz_for_display(quiz_data)
                    st.markdown(formatted_quiz)
                    
                    # Download button
                    st.download_button(
                        "📥 Download Quiz",
                        formatted_quiz,
                        f"quiz_lecture_{lecture_id}.md",
                        "text/markdown"
                    )
                
                tab_index += 1
            
            # Flashcards Tab
            if 'flashcards' in results:
                with selected_tabs[tab_index]:
                    st.subheader("Generated Flashcards")
                    
                    flashcard_data = results['flashcards']
                    formatted_flashcards = self.flashcard_generator.format_flashcards_for_display(flashcard_data)
                    st.markdown(formatted_flashcards)
                    
                    # Download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 Download Flashcards (Markdown)",
                            formatted_flashcards,
                            f"flashcards_lecture_{lecture_id}.md",
                            "text/markdown"
                        )
                    
                    with col2:
                        anki_format = self.flashcard_generator.create_anki_export(flashcard_data)
                        st.download_button(
                            "📥 Download for Anki",
                            anki_format,
                            f"flashcards_lecture_{lecture_id}_anki.txt",
                            "text/plain"
                        )
        
        # Success message
        st.success(f"🎉 Processing completed! Lecture saved with ID: {lecture_id}")
    
    def _format_summary_for_download(self, summary_data: Dict[str, Any]) -> str:
        """Format summary data for download."""
        text = f"# Lecture Summary\\n\\n"
        text += f"**Type:** {summary_data.get('type', 'N/A')}\\n\\n"
        text += f"## Summary\\n{summary_data['text']}\\n\\n"
        
        if summary_data.get('key_concepts'):
            text += f"## Key Concepts\\n"
            for concept in summary_data['key_concepts']:
                text += f"• {concept}\\n"
            text += "\\n"
        
        if summary_data.get('learning_objectives'):
            text += f"## Learning Objectives\\n"
            for objective in summary_data['learning_objectives']:
                text += f"• {objective}\\n"
        
        return text
    
    def view_saved_lectures_page(self):
        """Page for viewing saved lectures."""
        st.header("📚 Saved Lectures")
        
        lectures = self.db.get_all_lectures()
        
        if not lectures:
            st.info("No lectures saved yet. Upload and process an audio file to get started!")
            return
        
        # Search functionality
        search_query = st.text_input("🔍 Search lectures", placeholder="Search by filename or content...")
        
        if search_query:
            lectures = self.db.search_lectures(search_query)
        
        # Display lectures
        for lecture in lectures:
            with st.expander(f"📄 {lecture['filename']} (ID: {lecture['id']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Created:** {lecture['created_at']}")
                    st.write(f"**Updated:** {lecture['updated_at']}")
                    
                    if lecture['transcript']:
                        st.write("**Transcript preview:**")
                        preview = lecture['transcript'][:300] + "..." if len(lecture['transcript']) > 300 else lecture['transcript']
                        st.write(preview)
                
                with col2:
                    # Action buttons
                    if st.button(f"👁️ View Details", key=f"view_{lecture['id']}"):
                        self._show_lecture_details(lecture)
                    
                    if st.button(f"🗑️ Delete", key=f"delete_{lecture['id']}"):
                        if self.db.delete_lecture(lecture['id']):
                            st.success("Lecture deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete lecture")
    
    def _show_lecture_details(self, lecture: Dict[str, Any]):
        """Show detailed view of a lecture."""
        st.subheader(f"Lecture Details: {lecture['filename']}")
        
        # Create tabs for different content
        tabs = ["📝 Transcript"]
        if lecture['summary']:
            tabs.append("📄 Summary")
        if lecture['quiz']:
            tabs.append("❓ Quiz")
        if lecture['flashcards']:
            tabs.append("📚 Flashcards")
        
        selected_tabs = st.tabs(tabs)
        
        tab_index = 0
        
        # Transcript tab
        with selected_tabs[tab_index]:
            if lecture['transcript']:
                st.text_area("Transcript", lecture['transcript'], height=400)
                
                # Text insights
                insights = get_text_insights(lecture['transcript'])
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Words", insights['stats']['word_count'])
                with col2:
                    st.metric("Sentences", insights['stats']['sentence_count'])
                with col3:
                    st.metric("Reading Time", f"{insights['stats']['estimated_reading_time_minutes']:.1f}m")
                with col4:
                    st.metric("Speaking Time", f"{insights['stats']['estimated_speaking_time_minutes']:.1f}m")
            else:
                st.info("No transcript available")
        
        tab_index += 1
        
        # Summary tab
        if lecture['summary']:
            with selected_tabs[tab_index]:
                try:
                    summary_data = json.loads(lecture['summary']) if isinstance(lecture['summary'], str) else lecture['summary']
                    st.write(summary_data)
                except:
                    st.write(lecture['summary'])
            tab_index += 1
        
        # Quiz tab
        if lecture['quiz']:
            with selected_tabs[tab_index]:
                try:
                    quiz_data = json.loads(lecture['quiz']) if isinstance(lecture['quiz'], str) else lecture['quiz']
                    formatted_quiz = self.quiz_generator.format_quiz_for_display(quiz_data)
                    st.markdown(formatted_quiz)
                except:
                    st.write(lecture['quiz'])
            tab_index += 1
        
        # Flashcards tab
        if lecture['flashcards']:
            with selected_tabs[tab_index]:
                try:
                    flashcard_data = json.loads(lecture['flashcards']) if isinstance(lecture['flashcards'], str) else lecture['flashcards']
                    formatted_flashcards = self.flashcard_generator.format_flashcards_for_display(flashcard_data)
                    st.markdown(formatted_flashcards)
                except:
                    st.write(lecture['flashcards'])
    
    def batch_process_page(self):
        """Page for batch processing multiple files."""
        st.header("📁 Batch Process")
        st.info("Upload multiple audio files to process them all at once.")
        
        uploaded_files = st.file_uploader(
            "Choose audio files",
            type=[fmt.lstrip('.') for fmt in get_supported_audio_formats()],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.write(f"Selected {len(uploaded_files)} files")
            
            # Batch processing options
            col1, col2 = st.columns(2)
            with col1:
                model_size = st.selectbox("Model size:", ["tiny", "base", "small"], index=1)
                generate_summary = st.checkbox("Generate summaries", True)
            with col2:
                generate_quiz = st.checkbox("Generate quizzes", False)
                generate_flashcards = st.checkbox("Generate flashcards", False)
            
            if st.button("🚀 Process All Files", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Processing {file.name}...")
                    
                    try:
                        # Process each file (simplified version)
                        lecture_id = self.db.insert_lecture(filename=file.name)
                        
                        # Transcribe
                        transcription = self.speech_to_text.transcribe_audio(file)
                        cleaned_transcript = preprocess_audio_transcript(transcription['text'])
                        
                        # Generate content
                        results = self._generate_content(cleaned_transcript, generate_summary, generate_quiz, generate_flashcards)
                        
                        # Save to database
                        self.db.update_lecture(
                            lecture_id,
                            transcript=cleaned_transcript,
                            summary=json.dumps(results.get('summary', {})),
                            quiz=json.dumps(results.get('quiz', {})),
                            flashcards=json.dumps(results.get('flashcards', {}))
                        )
                        
                        st.success(f"✅ Processed: {file.name}")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to process {file.name}: {str(e)}")
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                status_text.text("All files processed!")
                st.success("🎉 Batch processing completed!")
    
    def settings_page(self):
        """Settings and configuration page."""
        st.header("⚙️ Settings")
        
        # API Configuration
        st.subheader("🔑 API Configuration")
        
        current_key = os.getenv('OPENAI_API_KEY', '')
        if current_key:
            st.success("✅ OpenAI API key is configured")
        else:
            st.error("❌ OpenAI API key not found")
            st.info("Please add your OpenAI API key to the .env file")
        
        # Model Settings
        st.subheader("🤖 Model Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Whisper Model Sizes:**")
            st.write("• **Tiny**: Fastest, least accurate")
            st.write("• **Base**: Good balance (recommended)")
            st.write("• **Small**: Better accuracy, slower")
            st.write("• **Medium**: High accuracy, much slower")
            st.write("• **Large**: Highest accuracy, very slow")
        
        with col2:
            st.write("**Supported Audio Formats:**")
            for fmt in get_supported_audio_formats():
                st.write(f"• {fmt}")
        
        # Database Info
        st.subheader("💾 Database Information")
        try:
            lectures = self.db.get_all_lectures()
            st.write(f"**Total lectures:** {len(lectures)}")
            
            if lectures:
                total_words = sum(len(lecture.get('transcript', '').split()) for lecture in lectures)
                st.write(f"**Total words transcribed:** {total_words:,}")
        except Exception as e:
            st.error(f"Database error: {str(e)}")
        
        # Clear data option
        st.subheader("🗑️ Data Management")
        if st.button("⚠️ Clear All Data", help="This will delete all saved lectures"):
            if st.checkbox("I understand this cannot be undone"):
                try:
                    lectures = self.db.get_all_lectures()
                    for lecture in lectures:
                        self.db.delete_lecture(lecture['id'])
                    st.success("All data cleared!")
                except Exception as e:
                    st.error(f"Failed to clear data: {str(e)}")


def main():
    """Main function to run the Streamlit app."""
    
    # Check for environment setup
    if not os.path.exists('.env'):
        st.error("❌ .env file not found. Please create it with your OpenAI API key.")
        st.info("Create a .env file in the project root with: OPENAI_API_KEY=your_api_key_here")
        return
    
    # Initialize and run the app
    app = LectureVoiceNotesApp()
    app.main()


if __name__ == "__main__":
    main()