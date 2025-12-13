import sys
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.product_parser_agent import ProductParserAgent
from agents.question_agent import QuestionAgent
from agents.block_agent import BlockAgent
from agents.comparison_agent import ComparisonAgent
from agents.assembly_agent import AssemblyAgent
from config import Config
from utils import load_json_file, logger

def main():
    try:
        Config.validate()
        logger.info("Configuration validated")
        
        llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=Config.TEMPERATURE
        )
        logger.info(f"Initialized LLM: {Config.MODEL_NAME}")
        
        parser_agent = ProductParserAgent(llm, max_retries=Config.MAX_RETRIES)
        question_agent = QuestionAgent(llm, max_retries=Config.MAX_RETRIES)
        block_agent = BlockAgent(llm, max_retries=Config.MAX_RETRIES)
        comparison_agent = ComparisonAgent(llm, max_retries=Config.MAX_RETRIES)
        assembly_agent = AssemblyAgent()
        logger.info("All agents initialized")
        
        input_path = Path(Config.INPUT_FILE)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {Config.INPUT_FILE}")
        
        raw_product = load_json_file(Config.INPUT_FILE)
        logger.info("Loaded input product data")
        
        parsed_product = parser_agent.execute(raw_product)
        logger.info("Product parsed successfully")
        
        questions = question_agent.execute(parsed_product)
        logger.info(f"Generated {len(questions)} questions")
        
        blocks = block_agent.execute(parsed_product)
        logger.info("Content blocks created")
        
        product_b, comparison = comparison_agent.execute(parsed_product)
        logger.info("Comparison product generated")
        
        assembly_agent.assemble_faq(
            questions,
            f"{Config.TEMPLATES_DIR}/faq_template.json",
            f"{Config.OUTPUT_DIR}/faq.json"
        )
        
        assembly_agent.assemble_product(
            parsed_product,
            blocks,
            f"{Config.TEMPLATES_DIR}/product_template.json",
            f"{Config.OUTPUT_DIR}/product_page.json"
        )
        
        assembly_agent.assemble_comparison(
            parsed_product,
            product_b,
            comparison,
            f"{Config.TEMPLATES_DIR}/comparison_template.json",
            f"{Config.OUTPUT_DIR}/comparison_page.json"
        )
        
        logger.info(f"All outputs generated successfully in {Config.OUTPUT_DIR}/")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()