"""
Quiz generation using OpenAI GPT models.
"""
import openai
import os
import json
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()


class QuizGenerator:
    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = None
        self._setup_openai()
    
    def _setup_openai(self):
        """Set up OpenAI API client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            st.error("OpenAI API key not found. Please check your .env file.")
            raise ValueError("OpenAI API key is required")
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            st.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    def generate_multiple_choice_quiz(self, text: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple choice quiz questions from the text.
        
        Args:
            text: The lecture transcript
            num_questions: Number of questions to generate
            
        Returns:
            List of quiz questions with options and answers
        """
        try:
            prompt = f"""
            Create {num_questions} multiple choice questions based on this lecture transcript:
            
            {text}
            
            Format each question as JSON with this structure:
            {{
                "question": "The question text",
                "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                "correct_answer": "A",
                "explanation": "Brief explanation of why this is correct"
            }}
            
            Make questions that test understanding of key concepts, not just memorization.
            Ensure incorrect options are plausible but clearly wrong.
            Return only a JSON array of questions.
            """
            
            with st.spinner(f'Generating {num_questions} multiple choice questions...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert educator who creates high-quality multiple choice questions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
            
            # Parse the JSON response
            quiz_content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            quiz_questions = self._parse_quiz_json(quiz_content)
            
            return quiz_questions[:num_questions]
            
        except Exception as e:
            st.error(f"Multiple choice quiz generation failed: {str(e)}")
            return []
    
    def generate_true_false_quiz(self, text: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """
        Generate true/false quiz questions from the text.
        
        Args:
            text: The lecture transcript
            num_questions: Number of questions to generate
            
        Returns:
            List of true/false questions
        """
        try:
            prompt = f"""
            Create {num_questions} true/false questions based on this lecture transcript:
            
            {text}
            
            Format each question as JSON:
            {{
                "question": "Statement to evaluate",
                "answer": true/false,
                "explanation": "Explanation of why this is true or false"
            }}
            
            Make statements that test understanding of key concepts.
            Mix true and false statements.
            Return only a JSON array of questions.
            """
            
            with st.spinner(f'Generating {num_questions} true/false questions...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert educator who creates effective true/false questions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
            
            quiz_content = response.choices[0].message.content.strip()
            quiz_questions = self._parse_quiz_json(quiz_content)
            
            return quiz_questions[:num_questions]
            
        except Exception as e:
            st.error(f"True/false quiz generation failed: {str(e)}")
            return []
    
    def generate_short_answer_quiz(self, text: str, num_questions: int = 3) -> List[Dict[str, Any]]:
        """
        Generate short answer questions from the text.
        
        Args:
            text: The lecture transcript
            num_questions: Number of questions to generate
            
        Returns:
            List of short answer questions
        """
        try:
            prompt = f"""
            Create {num_questions} short answer questions based on this lecture transcript:
            
            {text}
            
            Format each question as JSON:
            {{
                "question": "Question that requires a brief explanation",
                "sample_answer": "A good sample answer (2-3 sentences)",
                "key_points": ["key point 1", "key point 2", "key point 3"]
            }}
            
            Focus on questions that test conceptual understanding and application.
            Return only a JSON array of questions.
            """
            
            with st.spinner(f'Generating {num_questions} short answer questions...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert educator who creates thought-provoking short answer questions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
            
            quiz_content = response.choices[0].message.content.strip()
            quiz_questions = self._parse_quiz_json(quiz_content)
            
            return quiz_questions[:num_questions]
            
        except Exception as e:
            st.error(f"Short answer quiz generation failed: {str(e)}")
            return []
    
    def generate_fill_in_the_blanks(self, text: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        """
        Generate fill-in-the-blank questions from the text.
        
        Args:
            text: The lecture transcript
            num_questions: Number of questions to generate
            
        Returns:
            List of fill-in-the-blank questions
        """
        try:
            prompt = f"""
            Create {num_questions} fill-in-the-blank questions based on this lecture transcript:
            
            {text}
            
            Format each question as JSON:
            {{
                "question": "Statement with _____ representing the blank",
                "answer": "correct word or phrase for the blank",
                "context": "Brief context about this concept"
            }}
            
            Choose important terms or concepts for the blanks.
            Make sure the sentence flows naturally.
            Return only a JSON array of questions.
            """
            
            with st.spinner(f'Generating {num_questions} fill-in-the-blank questions...'):
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert educator who creates effective fill-in-the-blank questions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
            
            quiz_content = response.choices[0].message.content.strip()
            quiz_questions = self._parse_quiz_json(quiz_content)
            
            return quiz_questions[:num_questions]
            
        except Exception as e:
            st.error(f"Fill-in-the-blank quiz generation failed: {str(e)}")
            return []
    
    def generate_comprehensive_quiz(self, text: str, mc_questions: int = 3, 
                                   tf_questions: int = 2, sa_questions: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a comprehensive quiz with different question types.
        
        Args:
            text: The lecture transcript
            mc_questions: Number of multiple choice questions
            tf_questions: Number of true/false questions
            sa_questions: Number of short answer questions
            
        Returns:
            Dictionary with different types of questions
        """
        try:
            with st.spinner('Generating comprehensive quiz...'):
                quiz = {
                    'multiple_choice': self.generate_multiple_choice_quiz(text, mc_questions),
                    'true_false': self.generate_true_false_quiz(text, tf_questions),
                    'short_answer': self.generate_short_answer_quiz(text, sa_questions),
                }
            
            return quiz
            
        except Exception as e:
            st.error(f"Comprehensive quiz generation failed: {str(e)}")
            return {}
    
    def _parse_quiz_json(self, json_text: str) -> List[Dict[str, Any]]:
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
            # Fallback: try to create questions from text
            return self._fallback_question_parsing(json_text)
    
    def _fallback_question_parsing(self, text: str) -> List[Dict[str, Any]]:
        """Fallback method to parse questions when JSON parsing fails."""
        questions = []
        
        # Simple pattern matching for basic question extraction
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or line.endswith('.')):
                questions.append({
                    'question': line,
                    'type': 'text',
                    'note': 'Question extracted from text (formatting may be incomplete)'
                })
        
        return questions[:5]  # Limit to 5 questions
    
    def format_quiz_for_display(self, quiz: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Format quiz for display in Streamlit.
        
        Args:
            quiz: Dictionary with different types of questions
            
        Returns:
            Formatted quiz text
        """
        formatted_quiz = "# Generated Quiz\n\n"
        
        # Multiple Choice Questions
        if quiz.get('multiple_choice'):
            formatted_quiz += "## Multiple Choice Questions\n\n"
            for i, q in enumerate(quiz['multiple_choice'], 1):
                formatted_quiz += f"**{i}. {q.get('question', 'Question missing')}**\n\n"
                for option in q.get('options', []):
                    formatted_quiz += f"   {option}\n"
                formatted_quiz += f"\n*Correct Answer: {q.get('correct_answer', 'N/A')}*\n"
                formatted_quiz += f"*Explanation: {q.get('explanation', 'No explanation')}*\n\n"
        
        # True/False Questions
        if quiz.get('true_false'):
            formatted_quiz += "## True/False Questions\n\n"
            for i, q in enumerate(quiz['true_false'], 1):
                formatted_quiz += f"**{i}. {q.get('question', 'Question missing')}**\n\n"
                formatted_quiz += f"*Answer: {q.get('answer', 'N/A')}*\n"
                formatted_quiz += f"*Explanation: {q.get('explanation', 'No explanation')}*\n\n"
        
        # Short Answer Questions
        if quiz.get('short_answer'):
            formatted_quiz += "## Short Answer Questions\n\n"
            for i, q in enumerate(quiz['short_answer'], 1):
                formatted_quiz += f"**{i}. {q.get('question', 'Question missing')}**\n\n"
                formatted_quiz += f"*Sample Answer: {q.get('sample_answer', 'No sample answer')}*\n\n"
        
        return formatted_quiz


def get_quiz_types():
    """Get available quiz types."""
    return {
        'multiple_choice': 'Multiple Choice',
        'true_false': 'True/False',
        'short_answer': 'Short Answer',
        'fill_in_blanks': 'Fill in the Blanks',
        'comprehensive': 'Comprehensive (Mixed)'
    }


if __name__ == "__main__":
    # Test the quiz generator
    quiz_gen = QuizGenerator()
    print("Quiz generator initialized successfully!")
    
    test_text = "Machine learning is a subset of artificial intelligence that focuses on algorithms."
    mc_quiz = quiz_gen.generate_multiple_choice_quiz(test_text, 2)
    print(f"Generated {len(mc_quiz)} multiple choice questions")