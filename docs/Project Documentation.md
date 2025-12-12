# Project Documentation

## Problem Statement

The objective is to build an automated content generation system that transforms structured product data into multiple JSON-based output pages. The system must operate without manual content writing and instead derive all information through intelligent processing of input data.

The core challenge involves creating a system that can understand product specifications, generate relevant user questions, produce reusable content fragments, create comparative analysis against fictional alternatives, and assemble everything into machine-readable formats.

Traditional approaches rely on static scripts with hardcoded logic, making them inflexible and difficult to extend. This project requires an agentic framework where independent components collaborate through a language model to produce dynamic, contextually relevant content.

## Solution Overview

The solution implements a multi-agent system using LangChain as the orchestration framework and Google Gemini as the language model backend. Each agent is responsible for a distinct transformation step in the content generation pipeline.

The system accepts a single JSON file containing product specifications and produces three structured outputs: a product page highlighting key features and pricing, a comparison page contrasting the real product against a generated fictional alternative, and a categorized FAQ page addressing common user questions.

Unlike rule-based systems, this implementation leverages natural language understanding to interpret product data contextually. Each agent uses prompt engineering to guide the language model in generating appropriate content while maintaining consistency across outputs.

The architecture separates concerns into five specialized agents: parsing, question generation, content block creation, comparison analysis, and final assembly. This modular design ensures that modifications to one component do not cascade into others, supporting long-term maintainability.

## Scopes & Assumptions

### Scope

The system processes single-product JSON datasets containing fields such as name, concentration, skin type, ingredients, benefits, usage instructions, side effects, and price.

Output generation includes three mandatory JSON files: product page with highlights and pricing, comparison page with fictional competitor analysis, and FAQ page with minimum fifteen categorized questions.

The system operates entirely through API-based language model calls without requiring external databases, web scraping, or manual content databases.

All content generation must be deterministic given the same input, meaning identical product data always produces consistent outputs across multiple runs.

### Assumptions

Input JSON follows a predefined schema with known field names and data types. The system does not handle malformed or incomplete product data gracefully.

Template files define the structural shape of output JSON and remain static throughout execution. Changes to output format require template modifications but not agent logic changes.

The fictional comparison product must maintain structural similarity to the real product while differing in specific attributes like concentration, ingredients, and price.

Language model responses are expected to follow JSON formatting instructions. The system includes parsing logic to handle common formatting variations like markdown code blocks.

All agents execute sequentially under a single orchestrator without parallel processing or conditional branching based on intermediate results.

## System Design

### Architecture Overview

The system follows a pipeline architecture where data flows sequentially through five distinct agents. Each agent receives structured input, performs a specific transformation using the language model, and produces structured output for downstream consumption.

LangChain provides the foundational abstractions for agent creation, prompt management, and chain composition. The framework handles API communication with Google Gemini and manages response parsing.

The design prioritizes transparency and traceability. Every transformation step is explicit and isolated, making it possible to audit exactly how input data becomes final output.

### Agent Responsibilities

**ProductParserAgent** converts raw JSON into a normalized internal representation. This agent validates data types, ensures consistent field naming, and prepares the product model for downstream processing. It uses the language model to intelligently handle variations in input formatting while maintaining a standardized output structure.

**QuestionAgent** generates exactly fifteen user-facing questions with corresponding answers and category labels. Categories include informational, usage, safety, and purchase. The agent analyzes product attributes to formulate practical questions that users would genuinely ask about the product.

**BlockAgent** creates reusable content fragments representing benefits, usage instructions, ingredient lists, and pricing metadata. Each block is structured as either an array or object suitable for direct insertion into templates. This agent ensures content consistency across different output pages.

**ComparisonAgent** constructs a fictional competing product and computes structured comparison metrics. The fictional product maintains believability by following similar attribute patterns while introducing meaningful differences. Comparison fields include formulation strength, price differential, and suitability for specific skin types.

**AssemblyAgent** merges generated content with predefined templates to produce final JSON files. Unlike other agents, this component operates without language model calls, performing pure data structure manipulation. It loads templates, injects generated values, and writes formatted output files.

### Data Flow

The execution begins by loading the raw product JSON from the data directory. The ProductParserAgent receives this file and returns a normalized Python dictionary with validated fields and correct data types.

The normalized product model flows into three parallel processing paths handled by QuestionAgent, BlockAgent, and ComparisonAgent. Each produces its respective output structure independently.

QuestionAgent output consists of a list of dictionaries, each containing question text, answer text, and category label. BlockAgent output contains four distinct content fragments organized as a dictionary with keys for benefits, usage block, ingredients block, and price block.

ComparisonAgent returns two separate outputs: the fictional product B structure and a comparison dictionary containing calculated metrics between products A and B.

AssemblyAgent receives all generated content along with template file paths and output destination paths. It performs three assembly operations in sequence, producing the FAQ JSON, product page JSON, and comparison page JSON.

### Language Model Integration

All agents except AssemblyAgent utilize LangChain's LLMChain abstraction. Each agent defines a PromptTemplate specifying the exact instructions and expected output format.

Prompts are engineered to minimize ambiguity and maximize JSON compliance. Instructions explicitly state that responses must contain only valid JSON without markdown formatting, explanatory text, or additional commentary.

The system uses Gemini 2.5 Flash with temperature set to zero, ensuring deterministic outputs. Zero temperature forces the model to select the highest probability tokens at each step, eliminating random variation in responses.

Response parsing includes cleanup logic to strip markdown code fences, whitespace, and other common formatting artifacts before JSON deserialization. This makes the system robust to minor formatting inconsistencies in model outputs.

### Template System

Templates define the structural skeleton of output files using minimal JSON objects with empty values. The AssemblyAgent fills these templates by directly assigning generated content to specific keys.

The FAQ template contains a single key pointing to an empty array. The product template defines keys for name, highlights, usage block, ingredient block, and pricing. The comparison template establishes keys for product A, product B, and comparison metrics.

Templates are stored as static JSON files in the templates directory and loaded at runtime. This separation allows output format modifications without touching agent code, supporting rapid iteration on presentation requirements.

### Error Handling Strategy

The system assumes well-formed inputs and successful API responses. Production deployments would require comprehensive error handling including input validation, API timeout management, and malformed response detection.

Current implementation includes basic JSON parsing error recovery through string cleaning operations. If the language model wraps JSON in markdown code blocks, the parser strips these markers before deserialization.

Type coercion handles cases where numeric fields arrive as strings, particularly for price values. The ProductParserAgent explicitly converts string prices to integers after parsing.

### Extensibility Considerations

Adding new output formats requires creating a new template and corresponding assembly method. The agent pipeline remains unchanged, demonstrating separation between content generation and presentation.

Introducing additional content blocks involves extending the BlockAgent with new prompt instructions and updating templates to accommodate new fields. Other agents remain unaffected.

Supporting multiple products in a single run would require modifying the orchestrator to iterate over input files while reusing existing agent instances. Individual agent logic would not change.

Swapping language model providers requires changing only the LLM initialization in the orchestrator. Agent code references the abstract LLM interface provided by LangChain, making it provider-agnostic.

### Performance Characteristics

The system makes five language model API calls per execution: one for parsing, one for questions, one for blocks, one for comparison, and zero for assembly. Each call completes in approximately two to five seconds depending on response length.

Total execution time ranges from ten to twenty seconds for a single product, dominated by API latency rather than processing time. Batch processing multiple products would scale linearly with the number of inputs.

Output file sizes remain small, typically under five kilobytes per JSON file. The system generates no intermediate files, writing outputs only after complete assembly.

Memory footprint is minimal as all data remains in memory as Python objects until final file write operations. The system does not require database connections or persistent storage beyond the file system.

### System Limitations

The system cannot handle products outside the skincare domain without prompt modifications. Agent prompts contain domain-specific terminology and assumptions about product attributes.

Generated fictional comparison products may lack market realism as they are synthesized without reference to actual competitor data. The comparison serves structural demonstration purposes rather than accurate market analysis.

FAQ generation is limited to fifteen questions regardless of product complexity. More sophisticated products might warrant additional questions, while simpler products might need fewer.

The system provides no mechanism for human review or content refinement. Generated outputs are written directly to files without intermediate approval steps.

Content quality depends entirely on language model capabilities. Factually incorrect statements or poorly phrased questions cannot be detected or corrected automatically.