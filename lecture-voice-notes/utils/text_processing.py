"""
Text processing utilities for cleaning and formatting lecture transcripts.
"""
import re
import nltk
import string
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords', quiet=True)
    except:
        pass


class TextProcessor:
    def __init__(self):
        """Initialize the text processor."""
        self.stop_words = self._get_stop_words()
    
    def _get_stop_words(self) -> set:
        """Get English stop words."""
        try:
            from nltk.corpus import stopwords
            return set(stopwords.words('english'))
        except:
            # Fallback list of common stop words
            return {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
                'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
                'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
                'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
                'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
                'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
                'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
                'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                'under', 'again', 'further', 'then', 'once'
            }
    
    def clean_transcript(self, text: str) -> str:
        """
        Clean and format a raw transcript.
        
        Args:
            text: Raw transcript text
            
        Returns:
            Cleaned transcript
        """
        if not text or not text.strip():
            return ""
        
        cleaned_text = text
        
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Fix common transcription artifacts
        cleaned_text = self._fix_transcription_artifacts(cleaned_text)
        
        # Improve sentence structure
        cleaned_text = self._improve_sentence_structure(cleaned_text)
        
        # Clean up punctuation
        cleaned_text = self._clean_punctuation(cleaned_text)
        
        # Remove filler words
        cleaned_text = self._remove_filler_words(cleaned_text)
        
        return cleaned_text.strip()
    
    def _fix_transcription_artifacts(self, text: str) -> str:
        """Fix common transcription errors and artifacts."""
        
        # Remove timestamp-like patterns
        text = re.sub(r'\[\d{1,2}:\d{2}:\d{2}\]', '', text)
        text = re.sub(r'\(\d{1,2}:\d{2}:\d{2}\)', '', text)
        
        # Remove speaker labels if present
        text = re.sub(r'^(Speaker|Student|Professor|Lecturer)\s*\d*\s*:', '', text, flags=re.MULTILINE)
        text = re.sub(r'^(SPEAKER_\d+|UNKNOWN_\d+)\s*:', '', text, flags=re.MULTILINE)
        
        # Remove transcription confidence indicators
        text = re.sub(r'\[inaudible\]', '[unclear]', text, flags=re.IGNORECASE)
        text = re.sub(r'\[unclear\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[crosstalk\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[music\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[applause\]', '', text, flags=re.IGNORECASE)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s*([,.!?;:])', r'\1 \2', text)
        
        return text
    
    def _improve_sentence_structure(self, text: str) -> str:
        """Improve sentence structure and capitalization."""
        
        # Ensure sentences start with capital letters
        sentences = text.split('.')
        improved_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                improved_sentences.append(sentence)
        
        # Join back with proper spacing
        text = '. '.join(improved_sentences)
        
        # Fix spacing after sentence endings
        text = re.sub(r'([.!?])\s+', r'\1 ', text)
        
        # Ensure proper capitalization after sentence endings
        def capitalize_after_punct(match):
            return match.group(1) + ' ' + match.group(2).upper()
        
        text = re.sub(r'([.!?])\s+([a-z])', capitalize_after_punct, text)
        
        return text
    
    def _clean_punctuation(self, text: str) -> str:
        """Clean and standardize punctuation."""
        
        # Remove excessive punctuation
        text = re.sub(r'[,.!?;:]{2,}', '.', text)
        
        # Ensure space after punctuation
        text = re.sub(r'([,.!?;:])([A-Za-z])', r'\1 \2', text)
        
        # Remove punctuation at the beginning of sentences
        text = re.sub(r'\.\s*([,.!?;:])', r'. ', text)
        
        # Fix quotes
        text = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', text)
        text = re.sub(r"'\s*([^']*?)\s*'", r"'\1'", text)
        
        return text
    
    def _remove_filler_words(self, text: str) -> str:
        """Remove common filler words and phrases."""
        
        filler_patterns = [
            r'\b(um|uh|er|ah|like|you know|so|well|actually|basically|literally)\b',
            r'\b(kind of|sort of|type of)\b',
            r'\b(I mean|you see|let me see|let\'s see)\b',
            r'\b(right\?|okay\?|alright\?)\b'
        ]
        
        for pattern in filler_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces left by removed fillers
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        try:
            # Use NLTK if available
            from nltk.tokenize import sent_tokenize
            sentences = sent_tokenize(text)
        except:
            # Fallback: simple regex-based sentence splitting
            sentences = re.split(r'[.!?]+\s+', text)
        
        # Clean and filter sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short sentences
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """
        Extract key words and phrases from text.
        
        Args:
            text: Input text
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Convert to lowercase and remove punctuation
        text_lower = text.lower()
        text_clean = text_lower.translate(str.maketrans('', '', string.punctuation))
        
        # Split into words
        words = text_clean.split()
        
        # Filter out stop words and short words
        keywords = []
        for word in words:
            if (len(word) > 3 and 
                word not in self.stop_words and
                word.isalpha()):
                keywords.append(word)
        
        # Count word frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_keywords[:num_keywords]]
    
    def create_text_summary_stats(self, text: str) -> Dict[str, Any]:
        """
        Create summary statistics for text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with text statistics
        """
        if not text:
            return {}
        
        words = text.split()
        sentences = self.split_into_sentences(text)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Calculate readability (simple version)
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
        avg_chars_per_word = sum(len(word) for word in words) / len(words) if words else 0
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'character_count': len(text),
            'character_count_no_spaces': len(text.replace(' ', '')),
            'avg_words_per_sentence': round(avg_words_per_sentence, 1),
            'avg_chars_per_word': round(avg_chars_per_word, 1),
            'estimated_reading_time_minutes': round(len(words) / 200, 1),  # 200 WPM average
            'estimated_speaking_time_minutes': round(len(words) / 150, 1)   # 150 WPM speaking
        }
    
    def format_for_display(self, text: str, max_line_length: int = 80) -> str:
        """
        Format text for better display.
        
        Args:
            text: Input text
            max_line_length: Maximum characters per line
            
        Returns:
            Formatted text
        """
        sentences = self.split_into_sentences(text)
        
        formatted_lines = []
        current_line = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed line length, start new line
            if current_line and len(current_line) + len(sentence) + 1 > max_line_length:
                formatted_lines.append(current_line.strip())
                current_line = sentence + " "
            else:
                current_line += sentence + " "
        
        # Add the last line if it has content
        if current_line.strip():
            formatted_lines.append(current_line.strip())
        
        return '\n\n'.join(formatted_lines)
    
    def extract_topics(self, text: str, num_topics: int = 5) -> List[str]:
        """
        Extract main topics from text using simple keyword clustering.
        
        Args:
            text: Input text
            num_topics: Number of topics to extract
            
        Returns:
            List of topic phrases
        """
        # Extract keywords
        keywords = self.extract_keywords(text, 20)
        
        # Simple topic extraction based on keyword co-occurrence
        sentences = self.split_into_sentences(text)
        topic_candidates = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            keyword_count = sum(1 for keyword in keywords if keyword in sentence_lower)
            
            if keyword_count >= 2:  # Sentences with multiple keywords might indicate topics
                # Extract noun phrases (simple version)
                words = sentence.split()
                for i in range(len(words) - 1):
                    phrase = f"{words[i]} {words[i+1]}".lower()
                    if any(keyword in phrase for keyword in keywords):
                        topic_candidates.append(phrase)
        
        # Count frequency of topic candidates
        topic_freq = {}
        for topic in topic_candidates:
            topic_freq[topic] = topic_freq.get(topic, 0) + 1
        
        # Return top topics
        sorted_topics = sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, freq in sorted_topics[:num_topics] if freq > 1]


def preprocess_audio_transcript(transcript: str) -> str:
    """
    Main function to preprocess audio transcript for further processing.
    
    Args:
        transcript: Raw audio transcript
        
    Returns:
        Cleaned and formatted transcript
    """
    processor = TextProcessor()
    return processor.clean_transcript(transcript)


def get_text_insights(text: str) -> Dict[str, Any]:
    """
    Get comprehensive insights about the text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with text insights
    """
    processor = TextProcessor()
    
    return {
        'stats': processor.create_text_summary_stats(text),
        'keywords': processor.extract_keywords(text, 10),
        'topics': processor.extract_topics(text, 5),
        'sentences': processor.split_into_sentences(text)[:3]  # First 3 sentences
    }


if __name__ == "__main__":
    # Test the text processor
    processor = TextProcessor()
    print("Text processor initialized successfully!")
    
    test_text = "Um, this is like a test transcript, you know. It has um filler words and stuff."
    cleaned = processor.clean_transcript(test_text)
    print(f"Original: {test_text}")
    print(f"Cleaned: {cleaned}")
    
    stats = processor.create_text_summary_stats(cleaned)
    print(f"Stats: {stats}")
    
    keywords = processor.extract_keywords(cleaned)
    print(f"Keywords: {keywords}")