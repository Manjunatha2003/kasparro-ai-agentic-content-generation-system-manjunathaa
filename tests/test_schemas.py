import pytest
from pydantic import ValidationError
from schemas import Product, Question, PriceBlock, ContentBlocks, Comparison, FAQOutput

def test_product_valid():
    product = Product(
        name="Test Product",
        concentration="10%",
        skin_type=["Oily"],
        ingredients=["Vitamin C"],
        benefits=["Brightening"],
        usage="Apply daily",
        side_effects="None",
        price=500
    )
    assert product.price == 500
    assert product.name == "Test Product"

def test_product_invalid_price():
    with pytest.raises(ValidationError):
        Product(
            name="Test",
            concentration="10%",
            skin_type=["Oily"],
            ingredients=["Vitamin C"],
            benefits=["Brightening"],
            usage="Apply daily",
            side_effects="None",
            price=-100
        )

def test_product_empty_ingredients():
    with pytest.raises(ValidationError):
        Product(
            name="Test",
            concentration="10%",
            skin_type=["Oily"],
            ingredients=[],
            benefits=["Brightening"],
            usage="Apply daily",
            side_effects="None",
            price=500
        )

def test_question_valid():
    question = Question(
        question="What is this?",
        answer="It is a product",
        category="informational"
    )
    assert question.category == "informational"

def test_question_invalid_category():
    with pytest.raises(ValidationError):
        Question(
            question="What is this?",
            answer="It is a product",
            category="invalid_category"
        )

def test_price_block():
    price_block = PriceBlock(price=500, currency="INR")
    assert price_block.price == 500
    assert price_block.currency == "INR"

def test_content_blocks():
    blocks = ContentBlocks(
        benefits=["Benefit 1"],
        usage_block="Apply daily",
        ingredients_block=["Ingredient 1"],
        price_block=PriceBlock(price=500, currency="INR")
    )
    assert len(blocks.benefits) == 1

def test_faq_output_wrong_count():
    questions = [
        Question(question=f"Q{i}", answer=f"A{i}", category="informational")
        for i in range(10)
    ]
    with pytest.raises(ValidationError):
        FAQOutput(faqs=questions)

def test_faq_output_correct_count():
    questions = [
        Question(question=f"Q{i}", answer=f"A{i}", category="informational")
        for i in range(15)
    ]
    faq = FAQOutput(faqs=questions)
    assert len(faq.faqs) == 15