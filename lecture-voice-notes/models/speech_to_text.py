"""
Speech-to-text transcription using OpenAI Whisper.
"""
import whisper
import os
import tempfile
from typing import Optional, Dict, Any
from pydub import AudioSegment
import streamlit as st


class SpeechToText:
    def __init__(self, model_size: str = "base"):
        """
        Initialize the Whisper model.
        
        Args:
            model_size: Size of the Whisper model to use 
                       (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            with st.spinner(f'Loading Whisper {self.model_size} model...'):
                self.model = whisper.load_model(self.model_size)
        except Exception as e:
            st.error(f"Failed to load Whisper model: {str(e)}")
            raise
    
    def transcribe_audio(self, audio_file, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Audio file (path or file-like object)
            language: Language code (e.g., 'en', 'es', 'fr'). None for auto-detect
            
        Returns:
            Dictionary containing transcript and metadata
        """
        try:
            # Handle different input types
            if hasattr(audio_file, 'read'):
                # File-like object (e.g., Streamlit uploaded file)
                audio_path = self._save_temp_file(audio_file)
            else:
                # String path
                audio_path = audio_file
            
            # Convert to supported format if needed
            processed_audio_path = self._preprocess_audio(audio_path)
            
            # Transcribe using Whisper
            with st.spinner('Transcribing audio...'):
                if language:
                    result = self.model.transcribe(processed_audio_path, language=language)
                else:
                    result = self.model.transcribe(processed_audio_path)
            
            # Clean up temporary files
            if hasattr(audio_file, 'read'):
                os.remove(audio_path)
            if processed_audio_path != audio_path:
                os.remove(processed_audio_path)
            
            return {
                'text': result['text'].strip(),
                'segments': result['segments'],
                'language': result['language'],
                'duration': self._get_duration(result['segments'])
            }
            
        except Exception as e:
            st.error(f"Transcription failed: {str(e)}")
            raise
    
    def _save_temp_file(self, file_obj) -> str:
        """Save uploaded file to temporary location."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
            tmp_file.write(file_obj.read())
            return tmp_file.name
    
    def _preprocess_audio(self, audio_path: str) -> str:
        """
        Preprocess audio file to ensure compatibility with Whisper.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Path to processed audio file
        """
        try:
            # Get file extension
            _, ext = os.path.splitext(audio_path)
            ext = ext.lower()
            
            # If it's already in a supported format, return as is
            supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.mp4']
            if ext in supported_formats:
                return audio_path
            
            # Convert to WAV using pydub
            audio = AudioSegment.from_file(audio_path)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                wav_path = tmp_file.name
            
            # Export as WAV
            audio.export(wav_path, format="wav")
            
            return wav_path
            
        except Exception as e:
            st.warning(f"Audio preprocessing warning: {str(e)}")
            # Return original path if preprocessing fails
            return audio_path
    
    def _get_duration(self, segments: list) -> float:
        """Calculate total duration from segments."""
        if not segments:
            return 0.0
        return segments[-1]['end'] if segments else 0.0
    
    def transcribe_audio_with_timestamps(self, audio_file, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio with detailed timestamps.
        
        Args:
            audio_file: Audio file (path or file-like object)
            language: Language code (e.g., 'en', 'es', 'fr'). None for auto-detect
            
        Returns:
            Dictionary containing transcript with timestamps
        """
        result = self.transcribe_audio(audio_file, language)
        
        # Format segments with timestamps
        timestamped_segments = []
        for segment in result['segments']:
            timestamped_segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'id': segment['id']
            })
        
        return {
            'full_text': result['text'],
            'segments': timestamped_segments,
            'language': result['language'],
            'duration': result['duration']
        }
    
    def get_transcript_summary_stats(self, transcript: str) -> Dict[str, Any]:
        """
        Get basic statistics about the transcript.
        
        Args:
            transcript: The transcript text
            
        Returns:
            Dictionary with statistics
        """
        words = transcript.split()
        sentences = transcript.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'character_count': len(transcript),
            'character_count_no_spaces': len(transcript.replace(' ', '')),
            'estimated_reading_time': len(words) / 200,  # Average reading speed
        }


# Utility functions for Streamlit app
def get_supported_audio_formats():
    """Get list of supported audio formats."""
    return ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4', '.avi', '.mov']


def validate_audio_file(file) -> bool:
    """
    Validate if uploaded file is a supported audio format.
    
    Args:
        file: Streamlit uploaded file object
        
    Returns:
        True if valid, False otherwise
    """
    if file is None:
        return False
    
    file_extension = os.path.splitext(file.name)[1].lower()
    supported_formats = get_supported_audio_formats()
    
    return file_extension in supported_formats


if __name__ == "__main__":
    # Test the speech to text functionality
    stt = SpeechToText("base")
    print("Speech to text model loaded successfully!")
    print(f"Model size: {stt.model_size}")
    print(f"Supported formats: {get_supported_audio_formats()}")