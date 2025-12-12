import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class QuestionAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["product"],
            template="""Based on this product data, generate exactly 15 frequently asked questions with answers.

Product: {product}

Categories must be one of: informational, usage, safety, purchase

Each question should be practical and directly answerable from the product data.

Return ONLY a JSON array with this exact structure:
[
  {{"question": "...", "answer": "...", "category": "..."}},
  ...
]

No markdown, no explanations, only the JSON array with exactly 15 items."""
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
        
        questions = json.loads(cleaned)
        
        return questions