import json
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from schemas import Product
from utils import logger
import time

class ProductParserAgentLCEL:
    def __init__(self, llm, max_retries=3):
        self.llm = llm
        self.max_retries = max_retries
        self.parser = PydanticOutputParser(pydantic_object=Product)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a product data parser. Parse the input and return valid JSON."),
            ("user", """Parse this product data into the required format.

Product: {product_json}

{format_instructions}

Return only valid JSON matching the schema.""")
        ])
        
        self.chain = (
            {"product_json": RunnablePassthrough(), 
             "format_instructions": lambda x: self.parser.get_format_instructions()}
            | self.prompt
            | self.llm
        )
    
    def execute(self, raw_product):
        for attempt in range(self.max_retries):
            try:
                logger.info(f"ProductParserAgentLCEL attempt {attempt + 1}")
                product_str = json.dumps(raw_product)
                result = self.chain.invoke(product_str)
                
                content = result.content if hasattr(result, 'content') else str(result)
                
                cleaned = content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                parsed = json.loads(cleaned)
                
                if isinstance(parsed.get("price"), str):
                    try:
                        parsed["price"] = int(parsed["price"])
                    except ValueError:
                        raise ValueError(f"Invalid price format: {parsed.get('price')}")
                
                product = Product(**parsed)
                logger.info("Product parsed with LCEL successfully")
                return product.dict()
                
            except Exception as e:
                logger.error(f"ProductParserAgentLCEL attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2)
        
        raise RuntimeError("ProductParserAgentLCEL failed after all retries")