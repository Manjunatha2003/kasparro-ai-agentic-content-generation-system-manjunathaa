import pytest
from pydantic import ValidationError
from schemas import FAQOutput, Question, Product

def test_hard_gate_faq_count_14_rejected():
    questions = [
        Question(question=f"Question {i}?", answer=f"Answer {i}", category="informational")
        for i in range(14)
    ]
    
    with pytest.raises(ValidationError) as exc_info:
        FAQOutput(faqs=questions)
    
    assert "Expected 15 FAQs" in str(exc_info.value)

def test_hard_gate_faq_count_16_rejected():
    questions = [
        Question(question=f"Question {i}?", answer=f"Answer {i}", category="informational")
        for i in range(16)
    ]
    
    with pytest.raises(ValidationError) as exc_info:
        FAQOutput(faqs=questions)
    
    assert "Expected 15 FAQs" in str(exc_info.value)

def test_hard_gate_faq_count_15_accepted():
    questions = [
        Question(question=f"Question {i}?", answer=f"Answer {i}", category="informational")
        for i in range(15)
    ]
    
    faq = FAQOutput(faqs=questions)
    assert len(faq.faqs) == 15

def test_hard_gate_price_zero_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="Test",
            concentration="10%",
            skin_type=["Oily"],
            ingredients=["Vitamin C"],
            benefits=["Brightening"],
            usage="Apply",
            side_effects="None",
            price=0
        )
    
    assert "Price must be positive" in str(exc_info.value)

def test_hard_gate_negative_price_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="Test",
            concentration="10%",
            skin_type=["Oily"],
            ingredients=["Vitamin C"],
            benefits=["Brightening"],
            usage="Apply",
            side_effects="None",
            price=-100
        )
    
    assert "Price must be positive" in str(exc_info.value)

def test_hard_gate_empty_ingredients_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="Test",
            concentration="10%",
            skin_type=["Oily"],
            ingredients=[],
            benefits=["Brightening"],
            usage="Apply",
            side_effects="None",
            price=500
        )
    
    assert "List cannot be empty" in str(exc_info.value)

def test_hard_gate_empty_benefits_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="Test",
            concentration="10%",
            skin_type=["Oily"],
            ingredients=["Vitamin C"],
            benefits=[],
            usage="Apply",
            side_effects="None",
            price=500
        )
    
    assert "List cannot be empty" in str(exc_info.value)

def test_hard_gate_invalid_category_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Question(
            question="What is this?",
            answer="A product",
            category="random_category"
        )
    
    assert "Category must be one of" in str(exc_info.value)

def test_hard_gate_valid_categories_accepted():
    valid_categories = ['informational', 'usage', 'safety', 'purchase']
    
    for category in valid_categories:
        question = Question(
            question="Test question?",
            answer="Test answer",
            category=category
        )
        assert question.category == category

def test_hard_gates_cannot_be_bypassed():
    invalid_data = {
        "faqs": [
            {"question": "Q1", "answer": "A1", "category": "informational"}
        ] * 10
    }
    
    with pytest.raises(ValidationError):
        FAQOutput(**invalid_data)
    
    with pytest.raises(ValidationError):
        FAQOutput.parse_obj(invalid_data)

def test_hard_gate_enforcement_at_schema_level():
    from pydantic import validator
    
    with pytest.raises(ValidationError):
        Product(
            name="Test",
            concentration="10%",
            skin_type=[],
            ingredients=["Vitamin C"],
            benefits=["Brightening"],
            usage="Apply",
            side_effects="None",
            price=500
        )