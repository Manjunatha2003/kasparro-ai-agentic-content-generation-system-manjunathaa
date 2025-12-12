# Agentic Content Generation System

Multi-agent system that transforms structured product data into JSON-based content pages using LangChain and Google Gemini.

## Requirements

Python 3.8 or higher

Internet connection for API access

Google Gemini API key

## Installation

Install required packages:

```
pip install -r requirements.txt
```

## Configuration

Get your Gemini API key from aistudio.google.com

Click Get API Key button

Copy the generated key

Create a file named .env in the project root directory

Add your API key to the .env file:

```
GOOGLE_API_KEY=your_api_key_here
```

Replace your_api_key_here with your actual API key

## Project Structure

```
project/
├── .env
├── requirements.txt
├── run.py
├── agents/
│   ├── product_parser_agent.py
│   ├── question_agent.py
│   ├── block_agent.py
│   ├── comparison_agent.py
│   └── assembly_agent.py
├── data/
│   └── input_product.json
├── templates/
│   ├── faq_template.json
│   ├── product_template.json
│   └── comparison_template.json
├── docs/
│   └── projectdocumentation.md
└── generated_output/
```

## Running the System

Execute the main script:

```
python run.py
```

The system will process the product data and display progress messages:

```
Product parsed successfully
Generated 15 questions
Content blocks created
Comparison product generated
All outputs generated successfully in generated_output/
```

## Output Files

After successful execution, three JSON files will be created in the generated_output directory:

faq.json contains categorized questions and answers

product_page.json contains product highlights and pricing

comparison_page.json contains product comparison data

## Input Format

The system expects a JSON file in the data directory with this structure:

```json
{
  "name": "Product Name",
  "concentration": "10% Active",
  "skin_type": ["Type1", "Type2"],
  "ingredients": ["Ingredient1", "Ingredient2"],
  "benefits": ["Benefit1", "Benefit2"],
  "usage": "Usage instructions",
  "side_effects": "Side effect information",
  "price": "699"
}
```

## Modifying Input Data

Edit data/input_product.json with your product information

Maintain the same field structure

Run the system again to generate new outputs

## API Usage

The system uses Google Gemini API which provides a free tier

Free tier includes 1500 requests per day

Each execution uses 4 API calls

Monitor your usage at aistudio.google.com

## Troubleshooting

If you see API key errors, verify your .env file exists and contains a valid key

If JSON parsing fails, ensure template files are properly formatted

If model errors occur, check that you have internet connectivity

If rate limits are exceeded, wait before running again

## Notes

The system requires internet access to call the Gemini API

Generated content is deterministic for the same input

Output quality depends on the language model capabilities

All outputs are machine-readable JSON format