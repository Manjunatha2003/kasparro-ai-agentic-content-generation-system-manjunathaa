import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.product_parser_agent import ProductParserAgent
from agents.question_agent import QuestionAgent
from agents.block_agent import BlockAgent
from agents.comparison_agent import ComparisonAgent
from agents.assembly_agent import AssemblyAgent

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

parser_agent = ProductParserAgent(llm)
question_agent = QuestionAgent(llm)
block_agent = BlockAgent(llm)
comparison_agent = ComparisonAgent(llm)
assembly_agent = AssemblyAgent()

with open("data/input_product.json", "r") as f:
    raw_product = json.load(f)

parsed_product = parser_agent.execute(raw_product)
print("Product parsed successfully")

questions = question_agent.execute(parsed_product)
print(f"Generated {len(questions)} questions")

blocks = block_agent.execute(parsed_product)
print("Content blocks created")

product_b, comparison = comparison_agent.execute(parsed_product)
print("Comparison product generated")

os.makedirs("generated_output", exist_ok=True)

assembly_agent.assemble_faq(
    questions,
    "templates/faq_template.json",
    "generated_output/faq.json"
)

assembly_agent.assemble_product(
    parsed_product,
    blocks,
    "templates/product_template.json",
    "generated_output/product_page.json"
)

assembly_agent.assemble_comparison(
    parsed_product,
    product_b,
    comparison,
    "templates/comparison_template.json",
    "generated_output/comparison_page.json"
)

print("All outputs generated successfully in generated_output/")