import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class ComparisonAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["product_a"],
            template="""Create a fictional competing product and comparison analysis.

Real Product A: {product_a}

Generate:
1. A fictional Product B with similar structure but different values
2. Comparison metrics between A and B

Return ONLY a JSON object with this exact structure:
{{
  "product_b": {{
    "name": "...",
    "concentration": "...",
    "ingredients": [...],
    "benefits": [...],
    "price": number
  }},
  "comparison": {{
    "stronger_formulation": "name of stronger product or empty string",
    "price_difference": number (A price minus B price),
    "better_for_oily_skin": "name of better product"
  }}
}}

No markdown, no explanations, only JSON."""
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def execute(self, product_a):
        product_str = json.dumps(product_a, indent=2)
        result = self.chain.run(product_a=product_str)
        
        cleaned = result.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        data = json.loads(cleaned)
        
        return data["product_b"], data["comparison"]