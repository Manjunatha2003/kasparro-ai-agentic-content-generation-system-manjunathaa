import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class ProductParserAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["product_json"],
            template="""Parse and normalize the following product JSON data.
Extract all fields and convert them to a clean structured format.
Ensure price is an integer.

Product JSON:
{product_json}

Return ONLY a valid JSON object with these exact keys: name, concentration, skin_type, ingredients, benefits, usage, side_effects, price.
No markdown, no explanations, only JSON."""
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def execute(self, raw_product):
        product_str = json.dumps(raw_product)
        result = self.chain.run(product_json=product_str)
        
        cleaned = result.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        parsed = json.loads(cleaned)
        
        if isinstance(parsed["price"], str):
            parsed["price"] = int(parsed["price"])
        
        return parsed