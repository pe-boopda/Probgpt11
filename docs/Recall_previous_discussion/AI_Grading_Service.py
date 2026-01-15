# backend/app/services/ai_grading_service.py
"""
AI-powered automatic grading service for text answers
Uses OpenAI GPT models for intelligent answer evaluation
"""

from typing import Dict, List, Any, Optional
import logging
import json
from sqlalchemy.orm import Session

# OpenAI
import openai
from openai import OpenAI

# NLP libraries for fallback
from difflib import SequenceMatcher
import re

from app.core.config import settings
from app.models.test import Question


logger = logging.getLogger(__name__)


class AIGradingService:
    """
    Service for AI-powered grading of text answers
    
    Features:
    - Semantic similarity checking using OpenAI
    - Keyword matching
    - Spelling tolerance
    - Multi-language support
    - Explanation generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI grading service"""
        self.api_key = api_key or settings.OPENAI_API_KEY
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("OpenAI API key not provided - AI grading disabled")
    
    # ==================== MAIN GRADING METHOD ====================
    
    def grade_text_answer(
        self,
        question: Question,
        student_answer: str,
        use_ai: bool = True,
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Grade a text answer
        
        Args:
            question: Question object with correct answer(s)
            student_answer: Student's text response
            use_ai: Use AI grading (True) or keyword matching (False)
            threshold: Minimum score to consider correct (0.0-1.0)
            
        Returns:
            {
                'is_correct': bool,
                'score': float (0.0-1.0),
                'feedback': str,
                'method': str (ai/keyword/exact),
                'matched_keywords': list,
                'suggestions': list
            }
        """
        # Get expected answers from metadata
        metadata = question.metadata or {}
        expected_answers = metadata.get('expected_answers', [])
        keywords = metadata.get('keywords', [])
        
        if not expected_answers and not keywords:
            logger.warning(f"Question {question.id} has no expected answers or keywords")
            return {
                'is_correct': None,
                'score': 0.0,
                'feedback': 'Requires manual grading - no evaluation criteria set',
                'method': 'none',
                'matched_keywords': [],
                'suggestions': []
            }
        
        # Clean student answer
        student_answer = student_answer.strip()
        
        if not student_answer:
            return {
                'is_correct': False,
                'score': 0.0,
                'feedback': 'No answer provided',
                'method': 'empty',
                'matched_keywords': [],
                'suggestions': []
            }
        
        # Try AI grading first
        if use_ai and self.enabled:
            result = self._grade_with_ai(
                question_text=question.question_text,
                expected_answers=expected_answers,
                student_answer=student_answer,
                keywords=keywords,
                threshold=threshold
            )
            
            if result:
                return result
        
        # Fallback to keyword matching
        return self._grade_with_keywords(
            expected_answers=expected_answers,
            student_answer=student_answer,
            keywords=keywords,
            threshold=threshold
        )
    
    # ==================== AI GRADING ====================
    
    def _grade_with_ai(
        self,
        question_text: str,
        expected_answers: List[str],
        student_answer: str,
        keywords: List[str],
        threshold: float
    ) -> Optional[Dict[str, Any]]:
        """Grade using OpenAI GPT model"""
        try:
            # Construct prompt
            prompt = self._build_grading_prompt(
                question_text=question_text,
                expected_answers=expected_answers,
                student_answer=student_answer,
                keywords=keywords
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational assessment assistant. Evaluate student answers fairly and provide constructive feedback."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistent grading
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Validate and format result
            score = float(result.get('score', 0))
            is_correct = score >= threshold
            
            return {
                'is_correct': is_correct,
                'score': score,
                'feedback': result.get('feedback', ''),
                'method': 'ai',
                'matched_keywords': result.get('matched_keywords', []),
                'suggestions': result.get('suggestions', []),
                'ai_reasoning': result.get('reasoning', '')
            }
            
        except Exception as e:
            logger.error(f"AI grading failed: {str(e)}")
            return None
    
    def _build_grading_prompt(
        self,
        question_text: str,
        expected_answers: List[str],
        student_answer: str,
        keywords: List[str]
    ) -> str:
        """Build prompt for AI grading"""
        expected_text = "\n".join([f"- {ans}" for ans in expected_answers])
        keywords_text = ", ".join(keywords) if keywords else "None specified"
        
        prompt = f"""
Evaluate the following student answer for correctness and quality.

QUESTION:
{question_text}

EXPECTED ANSWERS (any of these are acceptable):
{expected_text}

KEY CONCEPTS TO LOOK FOR:
{keywords_text}

STUDENT'S ANSWER:
{student_answer}

EVALUATION CRITERIA:
1. Semantic similarity to expected answers
2. Presence of key concepts/keywords
3. Factual accuracy
4. Clarity and completeness
5. Minor spelling/grammar errors should be tolerated

Respond with a JSON object in this exact format:
{{
    "score": <float between 0.0 and 1.0>,
    "feedback": "<constructive feedback for the student>",
    "matched_keywords": [<list of keywords found in answer>],
    "reasoning": "<brief explanation of the grade>",
    "suggestions": [<list of suggestions for improvement if score < 0.7>]
}}

Guidelines:
- Score 1.0: Perfect answer, contains all key points
- Score 0.7-0.9: Good answer, minor issues or missing details
- Score 0.4-0.6: Partial answer, some correct elements
- Score 0.0-0.3: Incorrect or irrelevant answer
- Be lenient with spelling and phrasing if the meaning is clear
"""
        return prompt
    
    # ==================== KEYWORD GRADING (FALLBACK) ====================
    
    def _grade_with_keywords(
        self,
        expected_answers: List[str],
        student_answer: str,
        keywords: List[str],
        threshold: float
    ) -> Dict[str, Any]:
        """Grade using keyword matching and fuzzy string matching"""
        student_lower = student_answer.lower()
        
        # Check exact match first
        for expected in expected_answers:
            if self._fuzzy_match(expected.lower(), student_lower) > 0.95:
                return {
                    'is_correct': True,
                    'score': 1.0,
                    'feedback': 'Correct answer',
                    'method': 'exact',
                    'matched_keywords': keywords,
                    'suggestions': []
                }
        
        # Check keyword presence
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in student_lower:
                matched_keywords.append(keyword)
        
        # Calculate score based on keyword coverage
        if keywords:
            keyword_score = len(matched_keywords) / len(keywords)
        else:
            keyword_score = 0.0
        
        # Check semantic similarity with expected answers
        max_similarity = 0.0
        for expected in expected_answers:
            similarity = self._fuzzy_match(expected.lower(), student_lower)
            max_similarity = max(max_similarity, similarity)
        
        # Combined score
        final_score = max(keyword_score, max_similarity)
        is_correct = final_score >= threshold
        
        # Generate feedback
        if is_correct:
            feedback = f"Good answer. Matched {len(matched_keywords)} key concepts."
        else:
            missing = [kw for kw in keywords if kw not in matched_keywords]
            feedback = f"Incomplete answer. Missing key concepts: {', '.join(missing)}"
        
        return {
            'is_correct': is_correct,
            'score': final_score,
            'feedback': feedback,
            'method': 'keyword',
            'matched_keywords': matched_keywords,
            'suggestions': [f"Include: {kw}" for kw in keywords if kw not in matched_keywords]
        }
    
    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """Calculate fuzzy string similarity (0.0-1.0)"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    # ==================== BATCH GRADING ====================
    
    def grade_text_answers_batch(
        self,
        answers: List[Dict[str, Any]],
        use_ai: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Grade multiple text answers in batch
        More efficient for API calls
        
        Args:
            answers: List of {'question': Question, 'student_answer': str}
            use_ai: Use AI grading
            
        Returns:
            List of grading results
        """
        results = []
        
        for item in answers:
            result = self.grade_text_answer(
                question=item['question'],
                student_answer=item['student_answer'],
                use_ai=use_ai
            )
            results.append(result)
        
        return results
    
    # ==================== PLAGIARISM DETECTION ====================
    
    def detect_plagiarism(
        self,
        student_answer: str,
        reference_texts: List[str],
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Detect potential plagiarism by comparing with reference texts
        
        Args:
            student_answer: Student's answer
            reference_texts: List of reference texts to check against
            threshold: Similarity threshold for plagiarism (0.0-1.0)
            
        Returns:
            {
                'is_plagiarized': bool,
                'max_similarity': float,
                'matched_sources': list,
                'suspicious_passages': list
            }
        """
        student_lower = student_answer.lower()
        
        max_similarity = 0.0
        matched_sources = []
        
        for idx, reference in enumerate(reference_texts):
            similarity = self._fuzzy_match(reference.lower(), student_lower)
            
            if similarity >= threshold:
                max_similarity = max(max_similarity, similarity)
                matched_sources.append({
                    'source_index': idx,
                    'similarity': similarity,
                    'excerpt': reference[:100] + "..."
                })
        
        # Find suspicious passages (long exact matches)
        suspicious_passages = self._find_suspicious_passages(
            student_answer,
            reference_texts
        )
        
        return {
            'is_plagiarized': max_similarity >= threshold,
            'max_similarity': max_similarity,
            'matched_sources': matched_sources,
            'suspicious_passages': suspicious_passages
        }
    
    def _find_suspicious_passages(
        self,
        student_answer: str,
        reference_texts: List[str],
        min_length: int = 20
    ) -> List[Dict[str, Any]]:
        """Find passages that are copied verbatim"""
        suspicious = []
        student_lower = student_answer.lower()
        
        for idx, reference in enumerate(reference_texts):
            reference_lower = reference.lower()
            
            # Find common substrings
            for i in range(len(student_lower) - min_length):
                for j in range(len(reference_lower) - min_length):
                    # Check for match
                    match_length = 0
                    while (i + match_length < len(student_lower) and 
                           j + match_length < len(reference_lower) and
                           student_lower[i + match_length] == reference_lower[j + match_length]):
                        match_length += 1
                    
                    if match_length >= min_length:
                        suspicious.append({
                            'source_index': idx,
                            'passage': student_answer[i:i+match_length],
                            'length': match_length
                        })
        
        return suspicious
    
    # ==================== ANSWER IMPROVEMENT SUGGESTIONS ====================
    
    def suggest_improvements(
        self,
        question_text: str,
        student_answer: str,
        expected_answers: List[str]
    ) -> List[str]:
        """
        Use AI to suggest how student can improve their answer
        
        Args:
            question_text: The question
            student_answer: Student's current answer
            expected_answers: Expected correct answers
            
        Returns:
            List of improvement suggestions
        """
        if not self.enabled:
            return ["AI suggestions unavailable - enable OpenAI API"]
        
        try:
            prompt = f"""
A student answered the following question. Provide 3-5 specific suggestions 
for how they can improve their answer.

QUESTION: {question_text}

STUDENT'S ANSWER: {student_answer}

EXPECTED ANSWER: {expected_answers[0] if expected_answers else 'N/A'}

Provide suggestions in JSON format:
{{
    "suggestions": [
        "Specific suggestion 1",
        "Specific suggestion 2",
        ...
    ]
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful teaching assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('suggestions', [])
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {str(e)}")
            return ["Error generating suggestions"]
    
    # ==================== ANSWER QUALITY METRICS ====================
    
    def analyze_answer_quality(
        self,
        student_answer: str
    ) -> Dict[str, Any]:
        """
        Analyze various quality metrics of an answer
        
        Returns:
            {
                'word_count': int,
                'sentence_count': int,
                'avg_word_length': float,
                'readability_score': float,
                'has_spelling_errors': bool,
                'complexity_level': str (simple/medium/complex)
            }
        """
        # Word count
        words = re.findall(r'\b\w+\b', student_answer)
        word_count = len(words)
        
        # Sentence count
        sentences = re.split(r'[.!?]+', student_answer)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Average word length
        avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
        
        # Simple readability score (Flesch-Kincaid approximation)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        readability = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_word_length
        
        # Complexity level
        if avg_word_length < 4 and avg_sentence_length < 10:
            complexity = 'simple'
        elif avg_word_length < 6 and avg_sentence_length < 20:
            complexity = 'medium'
        else:
            complexity = 'complex'
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'readability_score': round(readability, 2),
            'complexity_level': complexity
        }


# ==================== HELPER FUNCTIONS ====================

def create_ai_grading_service(api_key: Optional[str] = None) -> AIGradingService:
    """Factory function to create AI grading service"""
    return AIGradingService(api_key=api_key)