"""
Flashcard generation using OpenAI GPT models.
"""
import openai
import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()


class FlashcardGenerator:
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
    
    def generate_concept_flashcards(self, text: str, num_cards: int = 10) -> List[Dict[str, str]]:
        """
        Generate concept-based flashcards from the text.
        
        Args:
            text: The lecture transcript
            num_cards: Number of flashcards to generate
            
        Returns:
            List of flashcards with front and back content
        """
        try:
            prompt = f"""
            Create {num_cards} educational flashcards based on this lecture transcript:
            
            {text}
            
            Format each flashcard as JSON:
            {{
                "front": "Question or concept prompt",
                "back": "Answer or explanation",
                "difficulty": "easy/medium/hard",
                "category": "general category of this concept"
            }}
            
            Focus on key concepts, definitions, and important relationships.
            Make fronts concise but clear.
            Make backs informative but not too long.
            Return only a JSON array of flashcards.
            """
            
            with st.spinner(f'Generating {num_cards} concept flashcards...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert educator who creates effective study flashcards."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
            
            flashcard_content = response.choices[0].message.content.strip()
            flashcards = self._parse_flashcard_json(flashcard_content)
            
            return flashcards[:num_cards]
            
        except Exception as e:
            st.error(f"Concept flashcard generation failed: {str(e)}")
            return []
    
    def generate_definition_flashcards(self, text: str, num_cards: int = 8) -> List[Dict[str, str]]:
        """
        Generate definition-focused flashcards from the text.
        
        Args:
            text: The lecture transcript
            num_cards: Number of flashcards to generate
            
        Returns:
            List of definition flashcards
        """
        try:
            prompt = f"""
            Create {num_cards} definition flashcards based on this lecture transcript:
            
            {text}
            
            Format each flashcard as JSON:
            {{
                "front": "What is [term]?",
                "back": "Clear, concise definition",
                "term": "the key term being defined",
                "example": "optional example or context"
            }}
            
            Focus on important terms, concepts, and vocabulary from the lecture.
            Make definitions clear and accurate.
            Return only a JSON array of flashcards.
            """
            
            with st.spinner(f'Generating {num_cards} definition flashcards...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating clear, educational definition flashcards."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
            
            flashcard_content = response.choices[0].message.content.strip()
            flashcards = self._parse_flashcard_json(flashcard_content)
            
            return flashcards[:num_cards]
            
        except Exception as e:
            st.error(f"Definition flashcard generation failed: {str(e)}")
            return []
    
    def generate_application_flashcards(self, text: str, num_cards: int = 6) -> List[Dict[str, str]]:
        """
        Generate application/example-based flashcards from the text.
        
        Args:
            text: The lecture transcript
            num_cards: Number of flashcards to generate
            
        Returns:
            List of application flashcards
        """
        try:
            prompt = f"""
            Create {num_cards} application-focused flashcards based on this lecture transcript:
            
            {text}
            
            Format each flashcard as JSON:
            {{
                "front": "How would you apply [concept] in [scenario]?",
                "back": "Detailed explanation of application",
                "concept": "the main concept being applied",
                "scenario": "the application context"
            }}
            
            Focus on practical applications, examples, and problem-solving scenarios.
            Make applications realistic and relevant.
            Return only a JSON array of flashcards.
            """
            
            with st.spinner(f'Generating {num_cards} application flashcards...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating practical application flashcards."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1800,
                    temperature=0.4
                )
            
            flashcard_content = response.choices[0].message.content.strip()
            flashcards = self._parse_flashcard_json(flashcard_content)
            
            return flashcards[:num_cards]
            
        except Exception as e:
            st.error(f"Application flashcard generation failed: {str(e)}")
            return []
    
    def generate_comparison_flashcards(self, text: str, num_cards: int = 5) -> List[Dict[str, str]]:
        """
        Generate comparison-based flashcards from the text.
        
        Args:
            text: The lecture transcript
            num_cards: Number of flashcards to generate
            
        Returns:
            List of comparison flashcards
        """
        try:
            prompt = f"""
            Create {num_cards} comparison flashcards based on this lecture transcript:
            
            {text}
            
            Format each flashcard as JSON:
            {{
                "front": "Compare [concept A] and [concept B]",
                "back": "Clear comparison highlighting similarities and differences",
                "concept_a": "first concept",
                "concept_b": "second concept"
            }}
            
            Focus on comparing related concepts, methods, or ideas from the lecture.
            Make comparisons clear and educational.
            Return only a JSON array of flashcards.
            """
            
            with st.spinner(f'Generating {num_cards} comparison flashcards...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating comparative analysis flashcards."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
            
            flashcard_content = response.choices[0].message.content.strip()
            flashcards = self._parse_flashcard_json(flashcard_content)
            
            return flashcards[:num_cards]
            
        except Exception as e:
            st.error(f"Comparison flashcard generation failed: {str(e)}")
            return []
    
    def generate_comprehensive_flashcard_set(self, text: str, 
                                           concept_cards: int = 6,
                                           definition_cards: int = 4,
                                           application_cards: int = 3) -> Dict[str, List[Dict[str, str]]]:
        """
        Generate a comprehensive set of flashcards with different types.
        
        Args:
            text: The lecture transcript
            concept_cards: Number of concept flashcards
            definition_cards: Number of definition flashcards
            application_cards: Number of application flashcards
            
        Returns:
            Dictionary with different types of flashcards
        """
        try:
            with st.spinner('Generating comprehensive flashcard set...'):
                flashcard_set = {
                    'concepts': self.generate_concept_flashcards(text, concept_cards),
                    'definitions': self.generate_definition_flashcards(text, definition_cards),
                    'applications': self.generate_application_flashcards(text, application_cards),
                }
                
                # Add comparison flashcards if content is substantial
                if len(text.split()) > 500:
                    flashcard_set['comparisons'] = self.generate_comparison_flashcards(text, 2)
            
            return flashcard_set
            
        except Exception as e:
            st.error(f"Comprehensive flashcard generation failed: {str(e)}")
            return {}
    
    def _parse_flashcard_json(self, json_text: str) -> List[Dict[str, str]]:
        """Parse JSON from GPT response, handling potential formatting issues."""
        try:
            # Try to find JSON array in the response
            json_pattern = r'\[.*\]'
            json_match = re.search(json_pattern, json_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # If no array found, try parsing the whole response
                return json.loads(json_text)
                
        except json.JSONDecodeError as e:
            st.warning(f"JSON parsing error: {str(e)}")
            # Fallback: create simple flashcards from text
            return self._fallback_flashcard_parsing(json_text)
    
    def _fallback_flashcard_parsing(self, text: str) -> List[Dict[str, str]]:
        """Fallback method to parse flashcards when JSON parsing fails."""
        flashcards = []
        
        # Simple pattern to extract basic Q&A pairs
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i in range(0, len(lines) - 1, 2):
            if i + 1 < len(lines):
                front = lines[i].replace('**', '').replace('*', '').strip()
                back = lines[i + 1].replace('**', '').replace('*', '').strip()
                
                if front and back:
                    flashcards.append({
                        'front': front,
                        'back': back,
                        'type': 'auto-generated',
                        'note': 'Generated from text parsing (may need formatting)'
                    })
        
        return flashcards[:10]  # Limit to 10 flashcards
    
    def format_flashcards_for_display(self, flashcard_set: Dict[str, List[Dict[str, str]]]) -> str:
        """
        Format flashcards for display in Streamlit.
        
        Args:
            flashcard_set: Dictionary with different types of flashcards
            
        Returns:
            Formatted flashcard text
        """
        formatted_output = "# Generated Flashcards\n\n"
        
        # Concept Flashcards
        if flashcard_set.get('concepts'):
            formatted_output += "## Concept Flashcards\n\n"
            for i, card in enumerate(flashcard_set['concepts'], 1):
                formatted_output += f"### Card {i}\n"
                formatted_output += f"**Front:** {card.get('front', 'Missing')}\n\n"
                formatted_output += f"**Back:** {card.get('back', 'Missing')}\n"
                if card.get('difficulty'):
                    formatted_output += f"*Difficulty: {card['difficulty']}*\n"
                formatted_output += "\n---\n\n"
        
        # Definition Flashcards
        if flashcard_set.get('definitions'):
            formatted_output += "## Definition Flashcards\n\n"
            for i, card in enumerate(flashcard_set['definitions'], 1):
                formatted_output += f"### Card {i}\n"
                formatted_output += f"**Front:** {card.get('front', 'Missing')}\n\n"
                formatted_output += f"**Back:** {card.get('back', 'Missing')}\n"
                if card.get('example'):
                    formatted_output += f"*Example: {card['example']}*\n"
                formatted_output += "\n---\n\n"
        
        # Application Flashcards
        if flashcard_set.get('applications'):
            formatted_output += "## Application Flashcards\n\n"
            for i, card in enumerate(flashcard_set['applications'], 1):
                formatted_output += f"### Card {i}\n"
                formatted_output += f"**Front:** {card.get('front', 'Missing')}\n\n"
                formatted_output += f"**Back:** {card.get('back', 'Missing')}\n\n"
                formatted_output += "---\n\n"
        
        # Comparison Flashcards
        if flashcard_set.get('comparisons'):
            formatted_output += "## Comparison Flashcards\n\n"
            for i, card in enumerate(flashcard_set['comparisons'], 1):
                formatted_output += f"### Card {i}\n"
                formatted_output += f"**Front:** {card.get('front', 'Missing')}\n\n"
                formatted_output += f"**Back:** {card.get('back', 'Missing')}\n\n"
                formatted_output += "---\n\n"
        
        return formatted_output
    
    def create_anki_export(self, flashcard_set: Dict[str, List[Dict[str, str]]]) -> str:
        """
        Create Anki-compatible export format.
        
        Args:
            flashcard_set: Dictionary with flashcards
            
        Returns:
            Tab-separated values for Anki import
        """
        anki_format = ""
        
        # Combine all flashcards
        all_cards = []
        for card_type, cards in flashcard_set.items():
            for card in cards:
                all_cards.append({
                    'front': card.get('front', ''),
                    'back': card.get('back', ''),
                    'type': card_type
                })
        
        # Format for Anki (Front, Back, Type)
        for card in all_cards:
            front = card['front'].replace('\n', '<br>').replace('\t', ' ')
            back = card['back'].replace('\n', '<br>').replace('\t', ' ')
            card_type = card['type']
            
            anki_format += f"{front}\t{back}\t{card_type}\n"
        
        return anki_format


def get_flashcard_types():
    """Get available flashcard types."""
    return {
        'concepts': 'Concept Cards',
        'definitions': 'Definition Cards', 
        'applications': 'Application Cards',
        'comparisons': 'Comparison Cards',
        'comprehensive': 'Comprehensive Set'
    }


if __name__ == "__main__":
    # Test the flashcard generator
    flashcard_gen = FlashcardGenerator()
    print("Flashcard generator initialized successfully!")
    
    test_text = "Machine learning involves training algorithms on data to make predictions."
    concept_cards = flashcard_gen.generate_concept_flashcards(test_text, 3)
    print(f"Generated {len(concept_cards)} concept flashcards")