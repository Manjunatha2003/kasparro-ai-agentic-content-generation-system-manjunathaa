import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from schemas import Product, Comparison
from utils import parse_json_with_retry, logger
from logic.deterministic import (
    calculate_price_difference,
    compare_concentrations,
    determine_better_for_skin_type
)
import time

class ComparisonAgent:
    def __init__(self, llm, max_retries=3):
        self.llm = llm
        self.max_retries = max_retries
        self.prompt = PromptTemplate(
            input_variables=["product_a"],
            template="""Create a fictional competing product for comparison.

Real Product A: {product_a}

Generate only Product B with similar structure but different values.

Return ONLY a JSON object with this exact structure:
{{
  "name": "...",
  "concentration": "...",
  "skin_type": [...],
  "ingredients": [...],
  "benefits": [...],
  "usage": "...",
  "side_effects": "...",
  "price": number
}}

No markdown, no explanations, only JSON."""
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def execute(self, product_a):
        for attempt in range(self.max_retries):
            try:
                logger.info(f"ComparisonAgent attempt {attempt + 1}")
                product_str = json.dumps(product_a, indent=2)
                result = self.chain.run(product_a=product_str)
                
                parsed = parse_json_with_retry(result)
                
                if isinstance(parsed.get("price"), str):
                    try:
                        parsed["price"] = int(parsed["price"])
                    except ValueError:
                        raise ValueError(f"Invalid price format in product B")
                
                product_b = Product(**parsed)
                
                price_diff = calculate_price_difference(product_a["price"], product_b.price)
                
                concentration_result = compare_concentrations(
                    product_a.get("concentration", "0%"),
                    product_b.concentration
                )
                
                if concentration_result == "a":
                    stronger = product_a["name"]
                elif concentration_result == "b":
                    stronger = product_b.name
                else:
                    stronger = ""
                
                better_oily = determine_better_for_skin_type(product_a, product_b.dict(), "Oily")
                
                comparison = Comparison(
                    stronger_formulation=stronger,
                    price_difference=price_diff,
                    better_for_oily_skin=better_oily
                )
                
                logger.info("Comparison generated and validated successfully")
                return product_b.dict(), comparison.dict()
                
            except Exception as e:
                logger.error(f"ComparisonAgent attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2)
        
        raise RuntimeError("ComparisonAgent failed after all retries")