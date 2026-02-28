"""
Text summarization using OpenAI GPT models.
"""
import openai
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()


class TextSummarizer:
    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = None
        self._setup_openai()
    
    def _setup_openai(self):
        """Set up OpenAI API client."""
        api_key = get_api_key()
        if not api_key:
            st.error("OpenAI API key not found. Please check your .env file.")
            raise ValueError("OpenAI API key is required")
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            st.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    def generate_summary(self, text: str, summary_type: str = "comprehensive") -> str:
        """
        Generate a summary of the given text.
        
        Args:
            text: The text to summarize
            summary_type: Type of summary ('brief', 'comprehensive', 'bullet_points')
            
        Returns:
            Generated summary
        """
        if not text or not text.strip():
            return "No text provided for summarization."
        
        try:
            prompt = self._create_summary_prompt(text, summary_type)
            
            with st.spinner(f'Generating {summary_type} summary...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at summarizing lecture content and educational material."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Summary generation failed: {str(e)}")
            raise
    
    def _create_summary_prompt(self, text: str, summary_type: str) -> str:
        """Create appropriate prompt based on summary type."""
        base_prompt = f"Please summarize the following lecture transcript:\n\n{text}\n\n"
        
        if summary_type == "brief":
            return base_prompt + """
            Provide a brief summary in 2-3 sentences that captures the main topic and key points.
            """
        
        elif summary_type == "comprehensive":
            return base_prompt + """
            Provide a comprehensive summary that includes:
            1. Main topic and objectives
            2. Key concepts and definitions
            3. Important examples or case studies
            4. Main conclusions or takeaways
            
            Format the summary in clear paragraphs with headings if appropriate.
            """
        
        elif summary_type == "bullet_points":
            return base_prompt + """
            Provide a summary in bullet point format that includes:
            • Main topic
            • Key concepts (3-5 points)
            • Important examples (if any)
            • Key takeaways (2-3 points)
            
            Use clear, concise bullet points.
            """
        
        else:
            return base_prompt + "Provide a clear and informative summary of the main points."
    
    def generate_key_concepts(self, text: str) -> List[str]:
        """
        Extract key concepts from the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of key concepts
        """
        try:
            prompt = f"""
            Analyze the following lecture transcript and extract the key concepts, terms, and ideas:
            
            {text}
            
            Please provide a list of 5-10 key concepts or terms that are central to this lecture.
            Format each concept as a single line item.
            """
            
            with st.spinner('Extracting key concepts...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at identifying key concepts in educational content."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
            
            concepts_text = response.choices[0].message.content.strip()
            
            # Parse the response into a list
            concepts = [
                concept.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                for concept in concepts_text.split('\n')
                if concept.strip()
            ]
            
            return concepts[:10]  # Limit to 10 concepts
            
        except Exception as e:
            st.error(f"Key concept extraction failed: {str(e)}")
            return []
    
    def generate_learning_objectives(self, text: str) -> List[str]:
        """
        Generate learning objectives based on the lecture content.
        
        Args:
            text: The lecture transcript
            
        Returns:
            List of learning objectives
        """
        try:
            prompt = f"""
            Based on the following lecture transcript, generate 3-5 clear learning objectives 
            that students should be able to achieve after studying this material:
            
            {text}
            
            Format each objective starting with an action verb (understand, explain, analyze, etc.).
            Make them specific and measurable.
            """
            
            with st.spinner('Generating learning objectives...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an educational consultant expert at creating learning objectives."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.3
                )
            
            objectives_text = response.choices[0].message.content.strip()
            
            # Parse into list
            objectives = [
                obj.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                for obj in objectives_text.split('\n')
                if obj.strip()
            ]
            
            return objectives[:5]  # Limit to 5 objectives
            
        except Exception as e:
            st.error(f"Learning objective generation failed: {str(e)}")
            return []
    
    def generate_structured_notes(self, text: str) -> Dict[str, Any]:
        """
        Generate structured notes from the lecture transcript.
        
        Args:
            text: The lecture transcript
            
        Returns:
            Dictionary with structured notes
        """
        try:
            # Get different types of content
            summary = self.generate_summary(text, "comprehensive")
            key_concepts = self.generate_key_concepts(text)
            learning_objectives = self.generate_learning_objectives(text)
            
            return {
                'summary': summary,
                'key_concepts': key_concepts,
                'learning_objectives': learning_objectives,
                'word_count': len(text.split()),
                'estimated_study_time': len(text.split()) / 200 * 60  # minutes
            }
            
        except Exception as e:
            st.error(f"Structured notes generation failed: {str(e)}")
            return {}


class AdvancedSummarizer(TextSummarizer):
    """Extended summarizer with additional features."""
    
    def generate_topic_outline(self, text: str) -> str:
        """
        Generate a topic outline from the lecture.
        
        Args:
            text: The lecture transcript
            
        Returns:
            Topic outline as formatted text
        """
        try:
            prompt = f"""
            Create a detailed topic outline from this lecture transcript:
            
            {text}
            
            Format as a hierarchical outline with main topics and subtopics:
            I. Main Topic
               A. Subtopic
               B. Subtopic
            II. Main Topic
               A. Subtopic
               etc.
            """
            
            with st.spinner('Generating topic outline...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating academic outlines."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.3
                )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Topic outline generation failed: {str(e)}")
            return ""


def get_summary_types():
    """Get available summary types."""
    return {
        "brief": "Brief (2-3 sentences)",
        "comprehensive": "Comprehensive (detailed)",
        "bullet_points": "Bullet Points",
    }


if __name__ == "__main__":
    # Test the summarizer
    summarizer = TextSummarizer()
    print("Text summarizer initialized successfully!")
    
    test_text = "This is a test lecture about artificial intelligence and machine learning."
    summary = summarizer.generate_summary(test_text, "brief")
    print(f"Test summary: {summary}")
    
    concepts = summarizer.generate_key_concepts(test_text)
    print(f"Key concepts: {concepts}")