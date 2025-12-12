import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class BlockAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["product"],
            template="""Create content blocks for this product.

Product: {product}

Generate these blocks:
1. benefits: Array of benefit strings
2. usage_block: Single usage instruction string
3. ingredients_block: Array of ingredient strings
4. price_block: Object with price (number) and currency (always "INR")

Return ONLY a JSON object with these exact keys: benefits, usage_block, ingredients_block, price_block.
No markdown, no explanations, only JSON."""
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def execute(self, product):
        product_str = json.dumps(product, indent=2)
        result = self.chain.run(product=product_str)
        
        cleaned = result.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        blocks = json.loads(cleaned)
        
        return blocks