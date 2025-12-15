from typing import List, Dict

def extract_concentration_value(concentration_str: str) -> float:
    digits = ''.join(filter(str.isdigit, concentration_str))
    return float(digits) if digits else 0.0

def compare_concentrations(concentration_a: str, concentration_b: str) -> str:
    value_a = extract_concentration_value(concentration_a)
    value_b = extract_concentration_value(concentration_b)
    
    if value_a > value_b:
        return "a"
    elif value_b > value_a:
        return "b"
    else:
        return "equal"

def calculate_price_difference(price_a: int, price_b: int) -> int:
    return price_a - price_b

def determine_better_for_skin_type(product_a: Dict, product_b: Dict, skin_type: str) -> str:
    skin_types_a = product_a.get("skin_type", [])
    skin_types_b = product_b.get("skin_type", [])
    
    a_suitable = skin_type in skin_types_a
    b_suitable = skin_type in skin_types_b
    
    if a_suitable and not b_suitable:
        return product_a["name"]
    elif b_suitable and not a_suitable:
        return product_b["name"]
    elif a_suitable and b_suitable:
        return product_a["name"]
    else:
        return "Neither"

def validate_ingredient_overlap(ingredients_a: List[str], ingredients_b: List[str]) -> Dict[str, any]:
    set_a = set(i.lower().strip() for i in ingredients_a)
    set_b = set(i.lower().strip() for i in ingredients_b)
    
    common = set_a.intersection(set_b)
    unique_a = set_a - set_b
    unique_b = set_b - set_a
    
    return {
        "common_ingredients": list(common),
        "unique_to_a": list(unique_a),
        "unique_to_b": list(unique_b),
        "overlap_percentage": len(common) / len(set_a) * 100 if set_a else 0
    }

def normalize_price_format(price_value) -> int:
    if isinstance(price_value, int):
        return price_value
    if isinstance(price_value, str):
        digits = ''.join(filter(str.isdigit, price_value))
        if not digits:
            raise ValueError(f"Cannot extract price from: {price_value}")
        return int(digits)
    raise TypeError(f"Price must be int or str, got {type(price_value)}")

def categorize_price_range(price: int) -> str:
    if price < 500:
        return "Budget"
    elif price < 1000:
        return "Mid-range"
    elif price < 2000:
        return "Premium"
    else:
        return "Luxury"

def calculate_benefit_score(benefits: List[str]) -> int:
    return len(benefits) * 10