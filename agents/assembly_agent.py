import json

class AssemblyAgent:
    def assemble_faq(self, questions, template_path, output_path):
        with open(template_path, "r") as t:
            obj = json.load(t)
        obj["faqs"] = questions
        with open(output_path, "w") as f:
            json.dump(obj, f, indent=4)

    def assemble_product(self, model, blocks, template_path, output_path):
        with open(template_path, "r") as t:
            obj = json.load(t)
        obj["name"] = model["name"]
        obj["highlights"] = blocks["benefits"]
        obj["usage_block"] = blocks["usage_block"]
        obj["ingredient_block"] = blocks["ingredients_block"]
        obj["pricing"] = blocks["price_block"]
        with open(output_path, "w") as f:
            json.dump(obj, f, indent=4)

    def assemble_comparison(self, product_a, product_b, comparison, template_path, output_path):
        with open(template_path, "r") as t:
            obj = json.load(t)
        obj["product_a"] = product_a
        obj["product_b"] = product_b
        obj["comparison"] = comparison
        with open(output_path, "w") as f:
            json.dump(obj, f, indent=4)