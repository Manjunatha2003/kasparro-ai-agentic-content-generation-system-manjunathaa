import sys
from pathlib import Path
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.product_parser_agent import ProductParserAgent
from agents.question_agent import QuestionAgent
from agents.block_agent import BlockAgent
from agents.comparison_agent import ComparisonAgent
from agents.assembly_agent import AssemblyAgent
from quality.quality_enforcer import QualityEnforcer
from config import Config
from utils import load_json_file, logger

class RecoverableError(Exception):
    pass

class NonRecoverableError(Exception):
    pass

class PipelineOrchestrator:
    def __init__(self):
        self.output_files = []
        self.quality_enforcer = QualityEnforcer()
        
    def initialize_agents(self):
        try:
            Config.validate()
            logger.info("Configuration validated")
            
            llm = ChatGoogleGenerativeAI(
                model=Config.MODEL_NAME,
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=Config.TEMPERATURE
            )
            logger.info(f"Initialized LLM: {Config.MODEL_NAME}")
            
            self.parser_agent = ProductParserAgent(llm, max_retries=Config.MAX_RETRIES)
            self.question_agent = QuestionAgent(llm, max_retries=Config.MAX_RETRIES)
            self.block_agent = BlockAgent(llm, max_retries=Config.MAX_RETRIES)
            self.comparison_agent = ComparisonAgent(llm, max_retries=Config.MAX_RETRIES)
            self.assembly_agent = AssemblyAgent()
            logger.info("All agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise NonRecoverableError(f"Cannot initialize agents: {e}")
    
    def load_input(self, input_path: str) -> Dict[str, Any]:
        try:
            if not Path(input_path).exists():
                raise NonRecoverableError(f"Input file not found: {input_path}")
            
            raw_product = load_json_file(input_path)
            logger.info("Input product data loaded")
            return raw_product
            
        except Exception as e:
            logger.error(f"Failed to load input: {e}")
            raise NonRecoverableError(f"Input loading failed: {e}")
    
    def parse_product(self, raw_product: Dict[str, Any]) -> Dict[str, Any]:
        try:
            parsed = self.parser_agent.execute(raw_product)
            logger.info("Product parsed successfully")
            return parsed
            
        except Exception as e:
            logger.error(f"Product parsing failed after retries: {e}")
            raise NonRecoverableError(f"Cannot parse product: {e}")
    
    def generate_questions(self, product: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            questions = self.question_agent.execute(product)
            
            if len(questions) != 15:
                raise NonRecoverableError(f"FAQ count is {len(questions)}, must be exactly 15")
            
            deduplicated = self.quality_enforcer.deduplicate_questions(questions)
            
            if len(deduplicated) < 15:
                logger.warning(f"Deduplication reduced count to {len(deduplicated)}, regenerating...")
                raise RecoverableError("Question deduplication failed count check")
            
            scored_questions = self.quality_enforcer.score_questions(deduplicated)
            
            low_quality = [q for q in scored_questions if q['quality_score'] < 50]
            if low_quality:
                logger.warning(f"Found {len(low_quality)} low quality questions")
                raise RecoverableError("Low quality questions detected")
            
            logger.info(f"Generated and validated {len(deduplicated)} high-quality questions")
            return deduplicated
            
        except RecoverableError as e:
            logger.warning(f"Recoverable error in question generation: {e}")
            raise
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            raise NonRecoverableError(f"Cannot generate questions: {e}")
    
    def generate_blocks(self, product: Dict[str, Any]) -> Dict[str, Any]:
        try:
            blocks = self.block_agent.execute(product)
            logger.info("Content blocks created successfully")
            return blocks
            
        except Exception as e:
            logger.error(f"Block generation failed: {e}")
            raise NonRecoverableError(f"Cannot generate blocks: {e}")
    
    def generate_comparison(self, product: Dict[str, Any]) -> tuple:
        try:
            product_b, comparison = self.comparison_agent.execute(product)
            logger.info("Comparison generated successfully")
            return product_b, comparison
            
        except Exception as e:
            logger.error(f"Comparison generation failed: {e}")
            raise NonRecoverableError(f"Cannot generate comparison: {e}")
    
    def assemble_outputs(self, parsed_product, questions, blocks, product_b, comparison):
        output_paths = {
            'faq': f"{Config.OUTPUT_DIR}/faq.json",
            'product': f"{Config.OUTPUT_DIR}/product_page.json",
            'comparison': f"{Config.OUTPUT_DIR}/comparison_page.json"
        }
        
        self.output_files = list(output_paths.values())
        
        try:
            self.assembly_agent.assemble_faq(
                questions,
                f"{Config.TEMPLATES_DIR}/faq_template.json",
                output_paths['faq']
            )
            
            self.assembly_agent.assemble_product(
                parsed_product,
                blocks,
                f"{Config.TEMPLATES_DIR}/product_template.json",
                output_paths['product']
            )
            
            self.assembly_agent.assemble_comparison(
                parsed_product,
                product_b,
                comparison,
                f"{Config.TEMPLATES_DIR}/comparison_template.json",
                output_paths['comparison']
            )
            
            logger.info("All outputs assembled and validated successfully")
            
        except Exception as e:
            logger.error(f"Assembly failed: {e}")
            raise NonRecoverableError(f"Cannot assemble outputs: {e}")
    
    def cleanup_outputs(self):
        for output_file in self.output_files:
            if Path(output_file).exists():
                Path(output_file).unlink()
                logger.info(f"Cleaned up: {output_file}")
    
    def run(self, input_path: str):
        try:
            self.initialize_agents()
            
            raw_product = self.load_input(input_path)
            
            parsed_product = self.parse_product(raw_product)
            
            max_quality_attempts = 3
            for attempt in range(max_quality_attempts):
                try:
                    questions = self.generate_questions(parsed_product)
                    break
                except RecoverableError as e:
                    if attempt == max_quality_attempts - 1:
                        raise NonRecoverableError(f"Quality enforcement failed after {max_quality_attempts} attempts")
                    logger.warning(f"Quality attempt {attempt + 1} failed, retrying...")
                    continue
            
            blocks = self.generate_blocks(parsed_product)
            
            product_b, comparison = self.generate_comparison(parsed_product)
            
            self.assemble_outputs(parsed_product, questions, blocks, product_b, comparison)
            
            logger.info(f"Pipeline completed successfully. Outputs in {Config.OUTPUT_DIR}/")
            return True
            
        except NonRecoverableError as e:
            logger.error(f"NON-RECOVERABLE ERROR: {e}")
            self.cleanup_outputs()
            return False
            
        except Exception as e:
            logger.error(f"UNEXPECTED ERROR: {e}", exc_info=True)
            self.cleanup_outputs()
            return False

def main():
    orchestrator = PipelineOrchestrator()
    success = orchestrator.run(Config.INPUT_FILE)
    
    if not success:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()