import json
import time
import logging
from typing import Any, Dict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def clean_json_response(response: str) -> str:
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def parse_json_with_retry(response: str, max_attempts: int = 3) -> Dict[str, Any]:
    for attempt in range(max_attempts):
        try:
            cleaned = clean_json_response(response)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                raise
            time.sleep(1)
    raise ValueError("Failed to parse JSON after all attempts")

def calculate_price_difference(price_a: int, price_b: int) -> int:
    return price_a - price_b

def ensure_directory(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

def load_json_file(filepath: str) -> Dict[str, Any]:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        raise

def save_json_file(data: Dict[str, Any], filepath: str) -> None:
    try:
        ensure_directory(Path(filepath).parent)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Saved output to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {e}")
        raise