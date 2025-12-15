import pytest
from logic.deterministic import (
    extract_concentration_value,
    compare_concentrations,
    calculate_price_difference,
    determine_better_for_skin_type,
    validate_ingredient_overlap,
    normalize_price_format,
    categorize_price_range,
    calculate_benefit_score
)

def test_extract_concentration_value():
    assert extract_concentration_value("10%") == 10.0
    assert extract_concentration_value("5% Active") == 5.0
    assert extract_concentration_value("No digits") == 0.0

def test_compare_concentrations():
    assert compare_concentrations("10%", "5%") == "a"
    assert compare_concentrations("5%", "10%") == "b"
    assert compare_concentrations("10%", "10%") == "equal"

def test_calculate_price_difference():
    assert calculate_price_difference(1000, 800) == 200
    assert calculate_price_difference(500, 700) == -200

def test_determine_better_for_skin_type():
    product_a = {"name": "Product A", "skin_type": ["Oily", "Combination"]}
    product_b = {"name": "Product B", "skin_type": ["Dry"]}
    
    assert determine_better_for_skin_type(product_a, product_b, "Oily") == "Product A"
    assert determine_better_for_skin_type(product_a, product_b, "Dry") == "Product B"

def test_validate_ingredient_overlap():
    ingredients_a = ["Vitamin C", "Hyaluronic Acid"]
    ingredients_b = ["Vitamin C", "Retinol"]
    
    result = validate_ingredient_overlap(ingredients_a, ingredients_b)
    assert "vitamin c" in result["common_ingredients"]
    assert "hyaluronic acid" in result["unique_to_a"]
    assert "retinol" in result["unique_to_b"]

def test_normalize_price_format():
    assert normalize_price_format(500) == 500
    assert normalize_price_format("699") == 699
    assert normalize_price_format("Rs. 1200") == 1200

def test_normalize_price_format_invalid():
    with pytest.raises(ValueError):
        normalize_price_format("No numbers")

def test_categorize_price_range():
    assert categorize_price_range(300) == "Budget"
    assert categorize_price_range(750) == "Mid-range"
    assert categorize_price_range(1500) == "Premium"
    assert categorize_price_range(2500) == "Luxury"

def test_calculate_benefit_score():
    assert calculate_benefit_score(["Benefit1", "Benefit2"]) == 20
    assert calculate_benefit_score([]) == 0