from schemas import FAQOutput, ProductPageOutput, ComparisonOutput
from utils import load_json_file, save_json_file, logger

class AssemblyAgent:
    def assemble_faq(self, questions, template_path, output_path):
        try:
            template = load_json_file(template_path)
            template["faqs"] = questions
            faq_output = FAQOutput(**template)
            save_json_file(faq_output.dict(), output_path)
            logger.info("FAQ assembled successfully")
        except Exception as e:
            logger.error(f"FAQ assembly failed: {e}")
            raise

    def assemble_product(self, model, blocks, template_path, output_path):
        try:
            template = load_json_file(template_path)
            template["name"] = model["name"]
            template["highlights"] = blocks["benefits"]
            template["usage_block"] = blocks["usage_block"]
            template["ingredient_block"] = blocks["ingredients_block"]
            template["pricing"] = blocks["price_block"]
            product_output = ProductPageOutput(**template)
            save_json_file(product_output.dict(), output_path)
            logger.info("Product page assembled successfully")
        except Exception as e:
            logger.error(f"Product page assembly failed: {e}")
            raise

    def assemble_comparison(self, product_a, product_b, comparison, template_path, output_path):
        try:
            template = load_json_file(template_path)
            template["product_a"] = product_a
            template["product_b"] = product_b
            template["comparison"] = comparison
            comparison_output = ComparisonOutput(**template)
            save_json_file(comparison_output.dict(), output_path)
            logger.info("Comparison page assembled successfully")
        except Exception as e:
            logger.error(f"Comparison page assembly failed: {e}")
            raise