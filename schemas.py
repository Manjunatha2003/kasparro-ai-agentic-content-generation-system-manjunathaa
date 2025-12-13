from pydantic import BaseModel, Field, validator
from typing import List, Optional

class Product(BaseModel):
    name: str
    concentration: str
    skin_type: List[str]
    ingredients: List[str]
    benefits: List[str]
    usage: str
    side_effects: str
    price: int
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('ingredients', 'benefits', 'skin_type')
    def validate_lists(cls, v):
        if not v or len(v) == 0:
            raise ValueError('List cannot be empty')
        return v

class Question(BaseModel):
    question: str
    answer: str
    category: str
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['informational', 'usage', 'safety', 'purchase']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of {valid_categories}')
        return v

class PriceBlock(BaseModel):
    price: int
    currency: str = "INR"

class ContentBlocks(BaseModel):
    benefits: List[str]
    usage_block: str
    ingredients_block: List[str]
    price_block: PriceBlock

class Comparison(BaseModel):
    stronger_formulation: str
    price_difference: int
    better_for_oily_skin: str

class FAQOutput(BaseModel):
    faqs: List[Question]
    
    @validator('faqs')
    def validate_faq_count(cls, v):
        if len(v) != 15:
            raise ValueError(f'Expected 15 FAQs, got {len(v)}')
        return v

class ProductPageOutput(BaseModel):
    name: str
    highlights: List[str]
    usage_block: str
    ingredient_block: List[str]
    pricing: PriceBlock

class ComparisonOutput(BaseModel):
    product_a: Product
    product_b: Product
    comparison: Comparison