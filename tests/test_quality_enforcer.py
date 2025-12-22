import pytest
from quality.quality_enforcer import QualityEnforcer

def test_deduplication_removes_duplicate_questions():
    enforcer = QualityEnforcer()
    
    questions = [
        {"question": "What is this?", "answer": "A product", "category": "informational"},
        {"question": "What is this?", "answer": "A product", "category": "informational"},
        {"question": "How to use?", "answer": "Apply daily", "category": "usage"}
    ]
    
    result = enforcer.deduplicate_questions(questions)
    
    assert len(result) == 2
    assert result[0]["question"] == "What is this?"
    assert result[1]["question"] == "How to use?"

def test_deduplication_case_insensitive():
    enforcer = QualityEnforcer()
    
    questions = [
        {"question": "What is this?", "answer": "A", "category": "informational"},
        {"question": "WHAT IS THIS?", "answer": "B", "category": "informational"},
        {"question": "what is this?", "answer": "C", "category": "informational"}
    ]
    
    result = enforcer.deduplicate_questions(questions)
    
    assert len(result) == 1

def test_deduplication_preserves_order():
    enforcer = QualityEnforcer()
    
    questions = [
        {"question": "First?", "answer": "A", "category": "informational"},
        {"question": "Second?", "answer": "B", "category": "usage"},
        {"question": "First?", "answer": "C", "category": "safety"}
    ]
    
    result = enforcer.deduplicate_questions(questions)
    
    assert len(result) == 2
    assert result[0]["question"] == "First?"
    assert result[1]["question"] == "Second?"

def test_quality_scoring_assigns_scores():
    enforcer = QualityEnforcer()
    
    questions = [
        {"question": "What are the benefits of this product?", "answer": "It brightens skin and reduces dark spots", "category": "informational"},
        {"question": "How?", "answer": "Use it", "category": "usage"}
    ]
    
    result = enforcer.score_questions(questions)
    
    assert all('quality_score' in q for q in result)
    assert result[0]['quality_score'] > result[1]['quality_score']

def test_quality_scoring_penalizes_short_questions():
    enforcer = QualityEnforcer()
    
    short_q = {"question": "Why?", "answer": "Because it works well", "category": "informational"}
    long_q = {"question": "Why is this product effective?", "answer": "Because it works well", "category": "informational"}
    
    short_result = enforcer._calculate_question_quality(short_q)
    long_result = enforcer._calculate_question_quality(long_q)
    
    assert long_result > short_result

def test_quality_scoring_penalizes_short_answers():
    enforcer = QualityEnforcer()
    
    short_a = {"question": "What is this product?", "answer": "Good", "category": "informational"}
    long_a = {"question": "What is this product?", "answer": "This is a premium vitamin C serum for brightening", "category": "informational"}
    
    short_result = enforcer._calculate_question_quality(short_a)
    long_result = enforcer._calculate_question_quality(long_a)
    
    assert long_result > short_result

def test_quality_scoring_requires_question_mark():
    enforcer = QualityEnforcer()
    
    no_mark = {"question": "What is this product", "answer": "A serum", "category": "informational"}
    with_mark = {"question": "What is this product?", "answer": "A serum", "category": "informational"}
    
    no_mark_score = enforcer._calculate_question_quality(no_mark)
    with_mark_score = enforcer._calculate_question_quality(with_mark)
    
    assert with_mark_score > no_mark_score

def test_quality_scoring_penalizes_identical_question_answer():
    enforcer = QualityEnforcer()
    
    identical = {"question": "Product", "answer": "Product", "category": "informational"}
    
    score = enforcer._calculate_question_quality(identical)
    
    assert score < 50

def test_block_quality_validation_requires_benefits():
    enforcer = QualityEnforcer()
    
    invalid_blocks = {"benefits": [], "ingredients_block": ["Vitamin C"], "usage_block": "Apply daily"}
    valid_blocks = {"benefits": ["Brightening", "Anti-aging"], "ingredients_block": ["Vitamin C"], "usage_block": "Apply daily"}
    
    assert not enforcer.validate_block_quality(invalid_blocks)
    assert enforcer.validate_block_quality(valid_blocks)

def test_block_quality_validation_requires_ingredients():
    enforcer = QualityEnforcer()
    
    invalid_blocks = {"benefits": ["Brightening"], "ingredients_block": [], "usage_block": "Apply daily"}
    
    assert not enforcer.validate_block_quality(invalid_blocks)

def test_block_quality_validation_requires_usage():
    enforcer = QualityEnforcer()
    
    invalid_blocks = {"benefits": ["Brightening"], "ingredients_block": ["Vitamin C"], "usage_block": ""}
    
    assert not enforcer.validate_block_quality(invalid_blocks)

def test_comparison_quality_detects_zero_price_difference():
    enforcer = QualityEnforcer()
    
    low_quality = {"price_difference": 0, "stronger_formulation": "Product A"}
    
    assert enforcer.detect_low_quality_comparison(low_quality)

def test_comparison_quality_detects_missing_stronger():
    enforcer = QualityEnforcer()
    
    low_quality = {"price_difference": 100, "stronger_formulation": ""}
    
    assert enforcer.detect_low_quality_comparison(low_quality)

def test_comparison_quality_accepts_valid_comparison():
    enforcer = QualityEnforcer()
    
    valid = {"price_difference": 100, "stronger_formulation": "Product A"}
    
    assert not enforcer.detect_low_quality_comparison(valid)