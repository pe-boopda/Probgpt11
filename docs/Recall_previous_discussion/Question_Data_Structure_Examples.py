# backend/examples/question_data_examples.py
"""
Examples of question data structures for all question types.
Use these as templates when creating questions.
"""

from typing import Dict, List, Any

# ==================== MATCHING QUESTION ====================

def create_matching_question_example() -> Dict[str, Any]:
    """
    Example: Match countries with their capitals
    """
    return {
        "question_type": "matching",
        "question_text": "Сопоставьте страны с их столицами",
        "points": 4.0,
        "image_id": None,
        "metadata": {
            "correct_matches": {
                "left_1": "right_1",  # Франция -> Париж
                "left_2": "right_2",  # Германия -> Берлин
                "left_3": "right_3",  # Италия -> Рим
                "left_4": "right_4",  # Испания -> Мадрид
            }
        },
        "options": [
            # Left column (items to match)
            {"option_text": "Франция", "is_correct": False, "order": 0, "match_id": "left_1"},
            {"option_text": "Германия", "is_correct": False, "order": 1, "match_id": "left_2"},
            {"option_text": "Италия", "is_correct": False, "order": 2, "match_id": "left_3"},
            {"option_text": "Испания", "is_correct": False, "order": 3, "match_id": "left_4"},
            
            # Right column (possible matches)
            {"option_text": "Париж", "is_correct": False, "order": 4, "match_id": "right_1"},
            {"option_text": "Берлин", "is_correct": False, "order": 5, "match_id": "right_2"},
            {"option_text": "Рим", "is_correct": False, "order": 6, "match_id": "right_3"},
            {"option_text": "Мадрид", "is_correct": False, "order": 7, "match_id": "right_4"},
        ]
    }

def matching_student_answer_example() -> Dict[str, Any]:
    """Student's answer for matching question"""
    return {
        "matches": {
            "left_1": "right_1",  # Франция -> Париж
            "left_2": "right_2",  # Германия -> Берлин
            "left_3": "right_3",  # Италия -> Рим
            "left_4": "right_4",  # Испания -> Мадрид
        }
    }


# ==================== ORDERING QUESTION ====================

def create_ordering_question_example() -> Dict[str, Any]:
    """
    Example: Order steps of scientific method
    """
    return {
        "question_type": "ordering",
        "question_text": "Расположите шаги научного метода в правильном порядке",
        "points": 3.0,
        "image_id": None,
        "metadata": {},
        "options": [
            # Options in CORRECT order (by 'order' field)
            {"option_text": "Наблюдение и формулирование вопроса", "is_correct": False, "order": 0},
            {"option_text": "Выдвижение гипотезы", "is_correct": False, "order": 1},
            {"option_text": "Проведение эксперимента", "is_correct": False, "order": 2},
            {"option_text": "Анализ данных", "is_correct": False, "order": 3},
            {"option_text": "Формулирование выводов", "is_correct": False, "order": 4},
        ]
    }

def ordering_student_answer_example() -> Dict[str, Any]:
    """Student's answer for ordering question"""
    # Student arranged in order: option_ids in the sequence they chose
    return {
        "order": [1, 2, 3, 4, 5]  # List of option IDs in chosen order
    }


# ==================== HOTSPOT QUESTION ====================

def create_hotspot_question_example() -> Dict[str, Any]:
    """
    Example: Click on specific organs in human body diagram
    """
    return {
        "question_type": "hotspot",
        "question_text": "Укажите на изображении: сердце, лёгкие и печень",
        "points": 3.0,
        "image_id": "abc123def456",  # Image of human body
        "metadata": {
            "correct_areas": [
                # Heart location (center-left, percentage coordinates)
                {"x": 45.0, "y": 35.0, "radius": 5.0, "label": "heart"},
                
                # Lungs location (left and right)
                {"x": 40.0, "y": 30.0, "radius": 6.0, "label": "lung_left"},
                {"x": 60.0, "y": 30.0, "radius": 6.0, "label": "lung_right"},
                
                # Liver location (right side)
                {"x": 55.0, "y": 45.0, "radius": 5.0, "label": "liver"},
            ],
            "tolerance": 5.0,  # How far from center is acceptable (in %)
            "min_clicks": 3,   # Minimum number of clicks required
            "max_clicks": 10,  # Maximum clicks allowed
        },
        "options": []  # No options for hotspot
    }

def hotspot_student_answer_example() -> Dict[str, Any]:
    """Student's answer for hotspot question"""
    return {
        "clicks": [
            {"id": 1, "x": 46.2, "y": 34.8, "timestamp": 1703601234},  # Near heart
            {"id": 2, "x": 41.5, "y": 29.3, "timestamp": 1703601238},  # Near left lung
            {"id": 3, "x": 59.1, "y": 31.2, "timestamp": 1703601242},  # Near right lung
            {"id": 4, "x": 54.8, "y": 46.5, "timestamp": 1703601246},  # Near liver
        ]
    }


# ==================== FILL BLANKS QUESTION ====================

def create_fill_blanks_question_example() -> Dict[str, Any]:
    """
    Example: Fill in historical dates and names
    """
    return {
        "question_type": "fill_blanks",
        "question_text": (
            "Вторая мировая война началась в ___ году, когда ___ напала на Польшу. "
            "Война закончилась в ___ году капитуляцией ___."
        ),
        "points": 4.0,
        "image_id": None,
        "metadata": {
            "correct_answers": {
                # Blank 0: year started
                "0": ["1939", "тысяча девятьсот тридцать девятом"],
                
                # Blank 1: country that attacked
                "1": ["Германия", "Нацистская Германия", "Третий Рейх"],
                
                # Blank 2: year ended
                "2": ["1945", "тысяча девятьсот сорок пятом"],
                
                # Blank 3: who surrendered
                "3": ["Германии", "Японии", "стран Оси"],
            },
            "case_sensitive": False,
            "exact_match": False,  # Allow partial matches
            "scoring": "all_or_nothing",  # or "partial" for partial credit
        },
        "options": []  # No options for fill blanks
    }

def fill_blanks_student_answer_example() -> Dict[str, Any]:
    """Student's answer for fill blanks question"""
    return {
        "blanks": {
            "0": "1939",
            "1": "Германия",
            "2": "1945",
            "3": "Германии",
        }
    }


# ==================== COMPLEX EXAMPLES ====================

def create_chemistry_matching_example() -> Dict[str, Any]:
    """
    More complex example: Chemical elements and symbols
    """
    return {
        "question_type": "matching",
        "question_text": "Сопоставьте химические элементы с их символами",
        "points": 5.0,
        "image_id": None,
        "metadata": {
            "correct_matches": {
                "left_1": "right_3",  # Водород -> H
                "left_2": "right_1",  # Кислород -> O
                "left_3": "right_5",  # Углерод -> C
                "left_4": "right_2",  # Азот -> N
                "left_5": "right_4",  # Натрий -> Na
            }
        },
        "options": [
            {"option_text": "Водород", "is_correct": False, "order": 0, "match_id": "left_1"},
            {"option_text": "Кислород", "is_correct": False, "order": 1, "match_id": "left_2"},
            {"option_text": "Углерод", "is_correct": False, "order": 2, "match_id": "left_3"},
            {"option_text": "Азот", "is_correct": False, "order": 3, "match_id": "left_4"},
            {"option_text": "Натрий", "is_correct": False, "order": 4, "match_id": "left_5"},
            
            {"option_text": "O", "is_correct": False, "order": 5, "match_id": "right_1"},
            {"option_text": "N", "is_correct": False, "order": 6, "match_id": "right_2"},
            {"option_text": "H", "is_correct": False, "order": 7, "match_id": "right_3"},
            {"option_text": "Na", "is_correct": False, "order": 8, "match_id": "right_4"},
            {"option_text": "C", "is_correct": False, "order": 9, "match_id": "right_5"},
        ]
    }

def create_cooking_ordering_example() -> Dict[str, Any]:
    """
    Example: Steps to bake a cake
    """
    return {
        "question_type": "ordering",
        "question_text": "Расположите шаги приготовления торта в правильном порядке",
        "points": 5.0,
        "image_id": None,
        "metadata": {},
        "options": [
            {"option_text": "Разогреть духовку до 180°C", "is_correct": False, "order": 0},
            {"option_text": "Смешать муку, сахар и яйца", "is_correct": False, "order": 1},
            {"option_text": "Добавить разрыхлитель и ванилин", "is_correct": False, "order": 2},
            {"option_text": "Залить тесто в форму", "is_correct": False, "order": 3},
            {"option_text": "Выпекать 30-40 минут", "is_correct": False, "order": 4},
            {"option_text": "Остудить и украсить", "is_correct": False, "order": 5},
        ]
    }

def create_anatomy_hotspot_example() -> Dict[str, Any]:
    """
    Example: Identify parts of the eye
    """
    return {
        "question_type": "hotspot",
        "question_text": "Укажите на диаграмме глаза: роговицу, радужку, зрачок и хрусталик",
        "points": 4.0,
        "image_id": "eye_diagram_123",
        "metadata": {
            "correct_areas": [
                {"x": 35.0, "y": 50.0, "radius": 4.0, "label": "cornea"},
                {"x": 45.0, "y": 50.0, "radius": 3.0, "label": "iris"},
                {"x": 47.0, "y": 50.0, "radius": 2.0, "label": "pupil"},
                {"x": 52.0, "y": 50.0, "radius": 3.0, "label": "lens"},
            ],
            "tolerance": 4.0,
            "min_clicks": 4,
            "max_clicks": 8,
            "show_labels": False,  # Don't show labels to student
        },
        "options": []
    }

def create_literature_fill_blanks_example() -> Dict[str, Any]:
    """
    Example: Complete a famous poem
    """
    return {
        "question_type": "fill_blanks",
        "question_text": (
            "У лукоморья ___ зелёный;\n"
            "Златая цепь на ___ том:\n"
            "И днём и ночью кот учёный\n"
            "Всё ходит по цепи ___"
        ),
        "points": 3.0,
        "image_id": None,
        "metadata": {
            "correct_answers": {
                "0": ["дуб", "дуб великолепный"],
                "1": ["дубе", "дубе том"],
                "2": ["кругом", "вокруг"],
            },
            "case_sensitive": False,
            "exact_match": False,
            "partial_credit": True,  # Award points for each correct blank
            "points_per_blank": 1.0,
        },
        "options": []
    }


# ==================== SQL INSERTION EXAMPLES ====================

def sql_insert_matching_question():
    """
    SQL example for inserting matching question
    """
    return """
    -- Insert the question
    INSERT INTO questions (
        test_id, question_type, question_text, 
        "order", points, metadata
    ) VALUES (
        1,  -- test_id
        'matching',
        'Сопоставьте страны с их столицами',
        1,  -- order
        4.0,
        '{"correct_matches": {"left_1": "right_1", "left_2": "right_2"}}'::jsonb
    ) RETURNING id;
    
    -- Insert options (8 total: 4 left + 4 right)
    INSERT INTO question_options (question_id, option_text, is_correct, "order", match_id)
    VALUES 
        (1, 'Франция', false, 0, 'left_1'),
        (1, 'Германия', false, 1, 'left_2'),
        (1, 'Париж', false, 4, 'right_1'),
        (1, 'Берлин', false, 5, 'right_2');
    """

def sql_insert_hotspot_question():
    """
    SQL example for inserting hotspot question
    """
    return """
    -- Insert the question
    INSERT INTO questions (
        test_id, question_type, question_text, 
        "order", points, image_id, metadata
    ) VALUES (
        1,  -- test_id
        'hotspot',
        'Укажите на изображении сердце и лёгкие',
        2,  -- order
        2.0,
        'body_diagram_123',
        '{
            "correct_areas": [
                {"x": 45.0, "y": 35.0, "radius": 5.0, "label": "heart"},
                {"x": 40.0, "y": 30.0, "radius": 6.0, "label": "lungs"}
            ],
            "tolerance": 5.0
        }'::jsonb
    );
    """


# ==================== API REQUEST EXAMPLES ====================

def api_create_matching_question():
    """
    Example API request to create matching question
    """
    return {
        "method": "POST",
        "url": "/api/tests/{test_id}/questions",
        "headers": {
            "Authorization": "Bearer {token}",
            "Content-Type": "application/json"
        },
        "body": {
            "question_type": "matching",
            "question_text": "Сопоставьте страны с их столицами",
            "order": 1,
            "points": 4.0,
            "image_id": None,
            "metadata": {
                "correct_matches": {
                    "left_1": "right_1",
                    "left_2": "right_2",
                }
            },
            "options": [
                {"option_text": "Франция", "is_correct": False, "order": 0, "match_id": "left_1"},
                {"option_text": "Германия", "is_correct": False, "order": 1, "match_id": "left_2"},
                {"option_text": "Париж", "is_correct": False, "order": 4, "match_id": "right_1"},
                {"option_text": "Берлин", "is_correct": False, "order": 5, "match_id": "right_2"},
            ]
        }
    }

def api_submit_hotspot_answer():
    """
    Example API request to submit hotspot answer
    """
    return {
        "method": "POST",
        "url": "/api/sessions/{session_id}/answer",
        "headers": {
            "Authorization": "Bearer {token}",
            "Content-Type": "application/json"
        },
        "body": {
            "question_id": 5,
            "answer_data": {
                "clicks": [
                    {"id": 1, "x": 46.2, "y": 34.8, "timestamp": 1703601234},
                    {"id": 2, "x": 41.5, "y": 29.3, "timestamp": 1703601238},
                ]
            }
        }
    }


# ==================== UTILITY FUNCTIONS ====================

def validate_matching_question(question_data: Dict[str, Any]) -> bool:
    """Validate matching question structure"""
    # Check metadata has correct_matches
    metadata = question_data.get("metadata", {})
    if "correct_matches" not in metadata:
        return False
    
    # Check options have match_id
    options = question_data.get("options", [])
    left_count = sum(1 for opt in options if opt.get("match_id", "").startswith("left_"))
    right_count = sum(1 for opt in options if opt.get("match_id", "").startswith("right_"))
    
    if left_count == 0 or right_count == 0:
        return False
    
    return True

def validate_hotspot_question(question_data: Dict[str, Any]) -> bool:
    """Validate hotspot question structure"""
    # Must have image
    if not question_data.get("image_id"):
        return False
    
    # Must have correct_areas in metadata
    metadata = question_data.get("metadata", {})
    if "correct_areas" not in metadata:
        return False
    
    correct_areas = metadata["correct_areas"]
    if not isinstance(correct_areas, list) or len(correct_areas) == 0:
        return False
    
    # Each area must have x, y, radius
    for area in correct_areas:
        if not all(k in area for k in ["x", "y", "radius"]):
            return False
    
    return True

def validate_fill_blanks_question(question_data: Dict[str, Any]) -> bool:
    """Validate fill blanks question structure"""
    # Question text must contain ___
    question_text = question_data.get("question_text", "")
    blank_count = question_text.count("___")
    
    if blank_count == 0:
        return False
    
    # Metadata must have correct_answers
    metadata = question_data.get("metadata", {})
    if "correct_answers" not in metadata:
        return False
    
    correct_answers = metadata["correct_answers"]
    if len(correct_answers) != blank_count:
        return False
    
    return True


if __name__ == "__main__":
    # Print examples
    print("=== MATCHING QUESTION ===")
    print(create_matching_question_example())
    print("\n=== ORDERING QUESTION ===")
    print(create_ordering_question_example())
    print("\n=== HOTSPOT QUESTION ===")
    print(create_hotspot_question_example())
    print("\n=== FILL BLANKS QUESTION ===")
    print(create_fill_blanks_question_example())