import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from schemas import ContentBlocks, PriceBlock
from utils import parse_json_with_retry, logger
import time

class BlockAgent:
    def __init__(self, llm, max_retries=3):
        self.llm = llm
        self.max_retries = max_retries
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
        for attempt in range(self.max_retries):
            try:
                logger.info(f"BlockAgent attempt {attempt + 1}")
                product_str = json.dumps(product, indent=2)
                result = self.chain.run(product=product_str)
                
                parsed = parse_json_with_retry(result)
                
                blocks = ContentBlocks(**parsed)
                logger.info("Content blocks created and validated successfully")
                return blocks.dict()
                
            except Exception as e:
                logger.error(f"BlockAgent attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2)
        
        raise RuntimeError("BlockAgent failed after all retries")