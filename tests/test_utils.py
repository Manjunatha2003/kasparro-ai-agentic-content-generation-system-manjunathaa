import pytest
import json
from utils import clean_json_response, parse_json_with_retry, calculate_price_difference

def test_clean_json_response_with_markdown():
    response = "```json\n{\"key\": \"value\"}\n```"
    cleaned = clean_json_response(response)
    assert cleaned == '{"key": "value"}'

def test_clean_json_response_plain():
    response = '{"key": "value"}'
    cleaned = clean_json_response(response)
    assert cleaned == '{"key": "value"}'

def test_parse_json_with_retry_valid():
    response = '{"name": "Product", "price": 500}'
    result = parse_json_with_retry(response)
    assert result["name"] == "Product"
    assert result["price"] == 500

def test_parse_json_with_retry_with_markdown():
    response = '```json\n{"name": "Product"}\n```'
    result = parse_json_with_retry(response)
    assert result["name"] == "Product"

def test_parse_json_with_retry_invalid():
    response = 'not json at all'
    with pytest.raises(ValueError):
        parse_json_with_retry(response)

def test_calculate_price_difference():
    diff = calculate_price_difference(1000, 800)
    assert diff == 200

def test_calculate_price_difference_negative():
    diff = calculate_price_difference(500, 700)
    assert diff == -200

def test_calculate_price_difference_zero():
    diff = calculate_price_difference(500, 500)
    assert diff == 0