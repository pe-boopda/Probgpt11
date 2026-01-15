# backend/tests/test_answer_checking.py
"""
Unit tests for answer checking logic in SessionService
"""

import pytest
import math
from typing import Dict, Any
from unittest.mock import Mock


class MockQuestion:
    """Mock Question object for testing"""
    def __init__(self, question_type: str, metadata: Dict[str, Any] = None, options: list = None):
        self.question_type = question_type
        self.metadata = metadata or {}
        self.options = options or []
        self.points = 1.0


class MockOption:
    """Mock QuestionOption object for testing"""
    def __init__(self, id: int, option_text: str, is_correct: bool = False, 
                 order: int = 0, match_id: str = None):
        self.id = id
        self.option_text = option_text
        self.is_correct = is_correct
        self.order = order
        self.match_id = match_id


# Import the checker methods (simplified versions for testing)
class AnswerChecker:
    """Simplified version of SessionService for testing"""
    
    @staticmethod
    def check_matching(question: MockQuestion, answer: Dict[str, Any]) -> bool:
        """Check matching question"""
        user_matches = answer.get("matches", {})
        
        if not user_matches:
            return False

        correct_pairs = question.metadata.get("correct_matches", {})
        
        if len(user_matches) != len(correct_pairs):
            return False

        for left_id, right_id in user_matches.items():
            if correct_pairs.get(left_id) != right_id:
                return False

        return True
    
    @staticmethod
    def check_ordering(question: MockQuestion, answer: Dict[str, Any]) -> bool:
        """Check ordering question"""
        user_order = answer.get("order", [])
        
        if not user_order:
            return False

        correct_order = [opt.id for opt in sorted(question.options, key=lambda x: x.order)]
        return user_order == correct_order
    
    @staticmethod
    def check_hotspot(question: MockQuestion, answer: Dict[str, Any]) -> bool:
        """Check hotspot question"""
        clicks = answer.get("clicks", [])
        
        if not clicks:
            return False

        correct_areas = question.metadata.get("correct_areas", [])
        tolerance = question.metadata.get("tolerance", 5)

        if not correct_areas:
            return False

        matched_areas = 0

        for area in correct_areas:
            area_x = area.get("x", 0)
            area_y = area.get("y", 0)
            area_radius = area.get("radius", tolerance)

            for click in clicks:
                click_x = click.get("x", 0)
                click_y = click.get("y", 0)

                distance = math.sqrt((click_x - area_x) ** 2 + (click_y - area_y) ** 2)

                if distance <= area_radius:
                    matched_areas += 1
                    break

        return matched_areas == len(correct_areas)
    
    @staticmethod
    def check_fill_blanks(question: MockQuestion, answer: Dict[str, Any]) -> bool:
        """Check fill blanks question"""
        user_blanks = answer.get("blanks", {})
        
        if not user_blanks:
            return False

        correct_answers = question.metadata.get("correct_answers", {})
        case_sensitive = question.metadata.get("case_sensitive", False)
        exact_match = question.metadata.get("exact_match", True)

        if not correct_answers:
            return False

        total_blanks = len(correct_answers)
        correct_blanks = 0

        for blank_id, user_answer in user_blanks.items():
            if blank_id not in correct_answers:
                continue

            expected_answers = correct_answers[blank_id]
            
            user_ans = user_answer.strip()
            if not case_sensitive:
                user_ans = user_ans.lower()

            for expected in expected_answers:
                exp_ans = expected.strip()
                if not case_sensitive:
                    exp_ans = exp_ans.lower()

                if exact_match:
                    if user_ans == exp_ans:
                        correct_blanks += 1
                        break
                else:
                    if exp_ans in user_ans or user_ans in exp_ans:
                        correct_blanks += 1
                        break

        return correct_blanks == total_blanks


# ==================== MATCHING TESTS ====================

def test_matching_correct_answer():
    """Test correct matching answer"""
    question = MockQuestion(
        question_type="matching",
        metadata={
            "correct_matches": {
                "left_1": "right_1",
                "left_2": "right_2",
                "left_3": "right_3",
            }
        }
    )
    
    answer = {
        "matches": {
            "left_1": "right_1",
            "left_2": "right_2",
            "left_3": "right_3",
        }
    }
    
    assert AnswerChecker.check_matching(question, answer) == True


def test_matching_incorrect_answer():
    """Test incorrect matching answer"""
    question = MockQuestion(
        question_type="matching",
        metadata={
            "correct_matches": {
                "left_1": "right_1",
                "left_2": "right_2",
            }
        }
    )
    
    answer = {
        "matches": {
            "left_1": "right_2",  # Wrong!
            "left_2": "right_1",  # Wrong!
        }
    }
    
    assert AnswerChecker.check_matching(question, answer) == False


def test_matching_incomplete_answer():
    """Test incomplete matching answer"""
    question = MockQuestion(
        question_type="matching",
        metadata={
            "correct_matches": {
                "left_1": "right_1",
                "left_2": "right_2",
                "left_3": "right_3",
            }
        }
    )
    
    answer = {
        "matches": {
            "left_1": "right_1",
            "left_2": "right_2",
            # Missing left_3!
        }
    }
    
    assert AnswerChecker.check_matching(question, answer) == False


# ==================== ORDERING TESTS ====================

def test_ordering_correct_answer():
    """Test correct ordering answer"""
    question = MockQuestion(
        question_type="ordering",
        options=[
            MockOption(id=1, option_text="Step 1", order=0),
            MockOption(id=2, option_text="Step 2", order=1),
            MockOption(id=3, option_text="Step 3", order=2),
        ]
    )
    
    answer = {
        "order": [1, 2, 3]
    }
    
    assert AnswerChecker.check_ordering(question, answer) == True


def test_ordering_incorrect_answer():
    """Test incorrect ordering answer"""
    question = MockQuestion(
        question_type="ordering",
        options=[
            MockOption(id=1, option_text="Step 1", order=0),
            MockOption(id=2, option_text="Step 2", order=1),
            MockOption(id=3, option_text="Step 3", order=2),
        ]
    )
    
    answer = {
        "order": [3, 2, 1]  # Reversed!
    }
    
    assert AnswerChecker.check_ordering(question, answer) == False


def test_ordering_partial_answer():
    """Test partial ordering answer"""
    question = MockQuestion(
        question_type="ordering",
        options=[
            MockOption(id=1, option_text="Step 1", order=0),
            MockOption(id=2, option_text="Step 2", order=1),
            MockOption(id=3, option_text="Step 3", order=2),
        ]
    )
    
    answer = {
        "order": [1, 2]  # Missing one!
    }
    
    assert AnswerChecker.check_ordering(question, answer) == False


# ==================== HOTSPOT TESTS ====================

def test_hotspot_correct_answer():
    """Test correct hotspot answer"""
    question = MockQuestion(
        question_type="hotspot",
        metadata={
            "correct_areas": [
                {"x": 45.0, "y": 60.0, "radius": 5.0},
                {"x": 80.0, "y": 30.0, "radius": 5.0},
            ],
            "tolerance": 5.0
        }
    )
    
    answer = {
        "clicks": [
            {"x": 46.0, "y": 61.0},  # Within tolerance of first area
            {"x": 79.0, "y": 31.0},  # Within tolerance of second area
        ]
    }
    
    assert AnswerChecker.check_hotspot(question, answer) == True


def test_hotspot_incorrect_answer():
    """Test incorrect hotspot answer"""
    question = MockQuestion(
        question_type="hotspot",
        metadata={
            "correct_areas": [
                {"x": 45.0, "y": 60.0, "radius": 5.0},
            ],
            "tolerance": 5.0
        }
    )
    
    answer = {
        "clicks": [
            {"x": 10.0, "y": 10.0},  # Far from correct area
        ]
    }
    
    assert AnswerChecker.check_hotspot(question, answer) == False


def test_hotspot_distance_calculation():
    """Test hotspot distance calculation"""
    question = MockQuestion(
        question_type="hotspot",
        metadata={
            "correct_areas": [
                {"x": 50.0, "y": 50.0, "radius": 5.0},
            ],
            "tolerance": 5.0
        }
    )
    
    # Exactly 5 units away (should pass)
    answer_edge = {
        "clicks": [
            {"x": 53.0, "y": 54.0},  # Distance = 5
        ]
    }
    assert AnswerChecker.check_hotspot(question, answer_edge) == True
    
    # More than 5 units away (should fail)
    answer_far = {
        "clicks": [
            {"x": 56.0, "y": 56.0},  # Distance > 5
        ]
    }
    assert AnswerChecker.check_hotspot(question, answer_far) == False


def test_hotspot_multiple_areas():
    """Test hotspot with multiple correct areas"""
    question = MockQuestion(
        question_type="hotspot",
        metadata={
            "correct_areas": [
                {"x": 20.0, "y": 30.0, "radius": 5.0},
                {"x": 50.0, "y": 50.0, "radius": 5.0},
                {"x": 80.0, "y": 70.0, "radius": 5.0},
            ],
            "tolerance": 5.0
        }
    )
    
    answer = {
        "clicks": [
            {"x": 21.0, "y": 31.0},
            {"x": 51.0, "y": 49.0},
            {"x": 79.0, "y": 71.0},
        ]
    }
    
    assert AnswerChecker.check_hotspot(question, answer) == True


# ==================== FILL BLANKS TESTS ====================

def test_fill_blanks_correct_answer():
    """Test correct fill blanks answer"""
    question = MockQuestion(
        question_type="fill_blanks",
        metadata={
            "correct_answers": {
                "0": ["Paris", "paris"],
                "1": ["France", "france"],
            },
            "case_sensitive": False,
            "exact_match": True
        }
    )
    
    answer = {
        "blanks": {
            "0": "Paris",
            "1": "France",
        }
    }
    
    assert AnswerChecker.check_fill_blanks(question, answer) == True


def test_fill_blanks_case_insensitive():
    """Test fill blanks with case insensitive"""
    question = MockQuestion(
        question_type="fill_blanks",
        metadata={
            "correct_answers": {
                "0": ["Paris"],
            },
            "case_sensitive": False,
            "exact_match": True
        }
    )
    
    answer_lower = {"blanks": {"0": "paris"}}
    answer_upper = {"blanks": {"0": "PARIS"}}
    
    assert AnswerChecker.check_fill_blanks(question, answer_lower) == True
    assert AnswerChecker.check_fill_blanks(question, answer_upper) == True


def test_fill_blanks_case_sensitive():
    """Test fill blanks with case sensitive"""
    question = MockQuestion(
        question_type="fill_blanks",
        metadata={
            "correct_answers": {
                "0": ["Paris"],
            },
            "case_sensitive": True,
            "exact_match": True
        }
    )
    
    answer_correct = {"blanks": {"0": "Paris"}}
    answer_wrong = {"blanks": {"0": "paris"}}
    
    assert AnswerChecker.check_fill_blanks(question, answer_correct) == True
    assert AnswerChecker.check_fill_blanks(question, answer_wrong) == False


def test_fill_blanks_multiple_alternatives():
    """Test fill blanks with multiple acceptable answers"""
    question = MockQuestion(
        question_type="fill_blanks",
        metadata={
            "correct_answers": {
                "0": ["1917", "тысяча девятьсот семнадцатом", "17-м"],
            },
            "case_sensitive": False,
            "exact_match": True
        }
    )
    
    answer1 = {"blanks": {"0": "1917"}}
    answer2 = {"blanks": {"0": "тысяча девятьсот семнадцатом"}}
    answer3 = {"blanks": {"0": "17-м"}}
    answer_wrong = {"blanks": {"0": "1918"}}
    
    assert AnswerChecker.check_fill_blanks(question, answer1) == True
    assert AnswerChecker.check_fill_blanks(question, answer2) == True
    assert AnswerChecker.check_fill_blanks(question, answer3) == True
    assert AnswerChecker.check_fill_blanks(question, answer_wrong) == False


def test_fill_blanks_fuzzy_match():
    """Test fill blanks with fuzzy matching"""
    question = MockQuestion(
        question_type="fill_blanks",
        metadata={
            "correct_answers": {
                "0": ["revolution"],
            },
            "case_sensitive": False,
            "exact_match": False  # Fuzzy!
        }
    )
    
    answer_exact = {"blanks": {"0": "revolution"}}
    answer_partial = {"blanks": {"0": "the revolution occurred"}}  # Contains "revolution"
    answer_wrong = {"blanks": {"0": "evolution"}}  # Similar but not matching
    
    assert AnswerChecker.check_fill_blanks(question, answer_exact) == True
    assert AnswerChecker.check_fill_blanks(question, answer_partial) == True
    assert AnswerChecker.check_fill_blanks(question, answer_wrong) == False


def test_fill_blanks_incomplete_answer():
    """Test incomplete fill blanks answer"""
    question = MockQuestion(
        question_type="fill_blanks",
        metadata={
            "correct_answers": {
                "0": ["answer1"],
                "1": ["answer2"],
                "2": ["answer3"],
            },
            "case_sensitive": False,
            "exact_match": True
        }
    )
    
    answer = {
        "blanks": {
            "0": "answer1",
            "1": "answer2",
            # Missing blank 2!
        }
    }
    
    assert AnswerChecker.check_fill_blanks(question, answer) == False


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    print("Running answer checking tests...\n")
    
    # Matching tests
    print("=== MATCHING TESTS ===")
    test_matching_correct_answer()
    print("✓ Correct matching answer")
    test_matching_incorrect_answer()
    print("✓ Incorrect matching answer")
    test_matching_incomplete_answer()
    print("✓ Incomplete matching answer")
    
    # Ordering tests
    print("\n=== ORDERING TESTS ===")
    test_ordering_correct_answer()
    print("✓ Correct ordering answer")
    test_ordering_incorrect_answer()
    print("✓ Incorrect ordering answer")
    test_ordering_partial_answer()
    print("✓ Partial ordering answer")
    
    # Hotspot tests
    print("\n=== HOTSPOT TESTS ===")
    test_hotspot_correct_answer()
    print("✓ Correct hotspot answer")
    test_hotspot_incorrect_answer()
    print("✓ Incorrect hotspot answer")
    test_hotspot_distance_calculation()
    print("✓ Hotspot distance calculation")
    test_hotspot_multiple_areas()
    print("✓ Multiple hotspot areas")
    
    # Fill blanks tests
    print("\n=== FILL BLANKS TESTS ===")
    test_fill_blanks_correct_answer()
    print("✓ Correct fill blanks answer")
    test_fill_blanks_case_insensitive()
    print("✓ Case insensitive matching")
    test_fill_blanks_case_sensitive()
    print("✓ Case sensitive matching")
    test_fill_blanks_multiple_alternatives()
    print("✓ Multiple alternative answers")
    test_fill_blanks_fuzzy_match()
    print("✓ Fuzzy matching")
    test_fill_blanks_incomplete_answer()
    print("✓ Incomplete answer")
    
    print("\n" + "="*50)
    print("ALL TESTS PASSED! ✅")
    print("="*50)