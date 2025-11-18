# Training Data for AI Skills Development

A comprehensive collection of example prompts, sample datasets, and test cases designed to help train and fine-tune AI skills across multiple domains.

## 📋 Overview

This repository contains structured training data for developing AI capabilities in:
- Financial Analysis
- Code Analysis & Debugging
- Data Science & Machine Learning
- Customer Support
- Legal Document Analysis
- Medical Diagnosis
- Creative Writing
- Technical Documentation

## 🗂️ Directory Structure

```
training_data/
├── financial_analysis/
│   ├── financial_statements.json       # Sample company financials with analysis prompts
│   └── ratio_analysis_prompts.json     # Financial ratio exercises and scenarios
├── code_analysis/
│   └── bug_detection_examples.json     # Common bugs, code smells, and refactoring
├── data_science/
│   └── sample_datasets.json            # Datasets with EDA, ML, and analysis prompts
├── customer_support/
│   └── support_tickets.json            # Support scenarios with good/poor responses
├── legal_analysis/
│   └── contract_analysis.json          # Contract clauses with risk analysis
├── medical_diagnosis/
│   └── case_studies.json               # Clinical cases with diagnostic reasoning
├── creative_writing/
│   └── writing_prompts.json            # Creative writing exercises and examples
├── technical_documentation/
│   └── documentation_examples.json     # API docs, user guides, README templates
└── README.md                           # This file
```

## 🎯 Use Cases

### 1. **Training AI Models**
- Fine-tune language models on domain-specific tasks
- Create supervised learning datasets
- Develop few-shot learning examples
- Build evaluation benchmarks

### 2. **Skill Development**
- Practice financial analysis and ratio interpretation
- Learn bug detection and code review
- Develop data science and statistical analysis skills
- Improve customer communication and support skills
- Understand legal document review
- Practice clinical reasoning
- Enhance creative writing abilities
- Master technical documentation

### 3. **Testing & Evaluation**
- Benchmark AI model performance across domains
- Create test suites for skill validation
- Evaluate accuracy on structured problems
- Measure improvement over time

## 📊 Domain Details

### Financial Analysis
- **Files**: `financial_statements.json`, `ratio_analysis_prompts.json`
- **Content**:
  - Complete financial statements for 3 companies
  - 25+ ratio analysis prompts with solutions
  - Comparative analysis exercises
  - DuPont analysis, valuation metrics
- **Skills Covered**: Financial modeling, ratio analysis, investment analysis, financial statement interpretation

### Code Analysis
- **Files**: `bug_detection_examples.json`
- **Content**:
  - 10+ common bugs across Python, JavaScript, Java, Go
  - Security vulnerabilities (SQL injection, XSS, command injection)
  - Logic errors and performance issues
  - Code smell detection
  - Refactoring exercises
- **Skills Covered**: Bug detection, security analysis, code review, refactoring, best practices

### Data Science
- **Files**: `sample_datasets.json`
- **Content**:
  - 5 realistic datasets (e-commerce, real estate, marketing, IoT, NLP)
  - EDA prompts and expected insights
  - ML model building exercises (classification, regression, clustering, time series)
  - Feature engineering challenges
  - Data preprocessing exercises
- **Skills Covered**: Exploratory analysis, machine learning, statistics, data cleaning, model evaluation

### Customer Support
- **Files**: `support_tickets.json`
- **Content**:
  - 30+ support ticket scenarios
  - Examples of poor vs. excellent responses
  - Difficult situations (angry customers, unreasonable requests)
  - Response frameworks and templates
  - Tone analysis exercises
- **Skills Covered**: Customer communication, conflict resolution, empathy, problem-solving, professional writing

### Legal Analysis
- **Files**: `contract_analysis.json`
- **Content**:
  - Contract clause analysis (NDAs, employment, SaaS, leases)
  - Risk identification and mitigation
  - Negotiation strategies
  - Red flag detection
  - GDPR compliance examples
- **Skills Covered**: Contract review, legal reasoning, risk assessment, negotiation
- **Disclaimer**: Educational purposes only. Not legal advice.

### Medical Diagnosis
- **Files**: `case_studies.json`
- **Content**:
  - Clinical case presentations
  - Differential diagnosis exercises
  - Diagnostic reasoning frameworks
  - Treatment planning
  - Evidence-based medicine
- **Skills Covered**: Clinical reasoning, differential diagnosis, medical decision-making
- **Disclaimer**: Educational use only. Not for actual medical diagnosis.

### Creative Writing
- **Files**: `writing_prompts.json`
- **Content**:
  - 20+ writing prompts across genres
  - Examples of strong vs. weak writing
  - Technique demonstrations (dialogue, description, POV, metaphor)
  - Character development exercises
  - Revision and editing practice
- **Skills Covered**: Narrative writing, dialogue, description, character development, editing

### Technical Documentation
- **Files**: `documentation_examples.json`
- **Content**:
  - API documentation templates
  - User guide examples
  - README best practices
  - Architecture documentation
  - Writing improvement exercises
- **Skills Covered**: Technical writing, API documentation, user guides, clear communication

## 🚀 Getting Started

### Basic Usage

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ClaudeCodeFrameWork/training_data
   ```

2. **Load a dataset** (Python example):
   ```python
   import json

   with open('financial_analysis/financial_statements.json', 'r') as f:
       financial_data = json.load(f)

   # Access company data
   companies = financial_data['companies']
   prompts = financial_data['analysis_prompts']
   ```

3. **Use for training**:
   ```python
   # Example: Create training pairs from prompts
   training_pairs = []
   for prompt in prompts:
       training_pairs.append({
           'input': prompt['prompt'],
           'output': prompt['expected_output']
       })
   ```

### Advanced Usage

#### Fine-tuning Example
```python
# Prepare data for fine-tuning
from datasets import Dataset

# Load multiple domains
domains = ['financial_analysis', 'code_analysis', 'data_science']
all_data = []

for domain in domains:
    with open(f'{domain}/*.json') as f:
        data = json.load(f)
        # Extract prompts and expected outputs
        # Format for your specific model
        all_data.extend(format_for_training(data))

# Create Hugging Face dataset
dataset = Dataset.from_list(all_data)
```

#### Evaluation Suite
```python
# Use as evaluation benchmark
def evaluate_model(model, domain='financial_analysis'):
    with open(f'{domain}/*.json') as f:
        test_cases = json.load(f)

    results = []
    for case in test_cases['prompts']:
        prediction = model.generate(case['prompt'])
        score = evaluate_response(prediction, case['expected_output'])
        results.append(score)

    return {
        'accuracy': sum(results) / len(results),
        'domain': domain
    }
```

## 📐 Data Format

All data files follow a consistent JSON structure:

```json
{
  "metadata": {
    "domain": "domain_name",
    "data_type": "description",
    "version": "1.0",
    "description": "Detailed description",
    "example_count": 10
  },
  "examples": [
    {
      "id": "UNIQUE_ID",
      "category": "subcategory",
      "difficulty": "beginner|intermediate|advanced",
      "prompt": "The question or scenario",
      "solution": "Expected answer or approach",
      "explanation": "Why this solution works"
    }
  ]
}
```

## 🎓 Educational Approach

This training data emphasizes:

1. **Progressive Difficulty**: Examples range from beginner to advanced
2. **Explanatory Learning**: Not just answers, but WHY and HOW
3. **Real-World Scenarios**: Practical, realistic examples
4. **Best Practices**: Industry-standard approaches and techniques
5. **Common Pitfalls**: Examples of what NOT to do and why
6. **Multiple Perspectives**: Different approaches to the same problem

## 📊 Statistics

| Domain | Files | Examples | Total Prompts | Avg Difficulty |
|--------|-------|----------|---------------|----------------|
| Financial Analysis | 2 | 15 | 35+ | Intermediate |
| Code Analysis | 1 | 20 | 25+ | Intermediate |
| Data Science | 1 | 5 datasets | 20+ | Advanced |
| Customer Support | 1 | 30 | 40+ | Beginner-Intermediate |
| Legal Analysis | 1 | 15 | 20+ | Advanced |
| Medical Diagnosis | 1 | 10 | 15+ | Advanced |
| Creative Writing | 1 | 20 | 30+ | All Levels |
| Technical Docs | 1 | 15 | 20+ | Intermediate |

**Total**: 8 domains, 9 files, 130+ unique examples, 200+ training prompts

## 🔧 Customization

You can extend this training data by:

1. **Adding new domains**: Follow the existing structure
2. **Increasing difficulty**: Add advanced scenarios to existing domains
3. **Domain-specific variants**: Create industry-specific versions
4. **Localization**: Translate to other languages
5. **Format conversion**: Convert to CSV, XML, or other formats

### Template for New Domain

```json
{
  "metadata": {
    "domain": "your_domain",
    "data_type": "description",
    "version": "1.0",
    "description": "What this trains",
    "example_count": 0
  },
  "examples": [
    {
      "id": "EXAMPLE_001",
      "category": "subcategory",
      "difficulty": "beginner",
      "prompt": "Your training prompt",
      "expected_output": {
        "answer": "Expected response",
        "explanation": "Why this is correct"
      }
    }
  ]
}
```

## ⚠️ Important Disclaimers

- **Medical**: For educational purposes only. Not for actual diagnosis or treatment.
- **Legal**: Not legal advice. Consult qualified attorney for legal matters.
- **Financial**: Educational examples. Not investment advice.
- **Code Examples**: Some examples intentionally show bad practices for teaching purposes.

## 🤝 Contributing

To contribute new training data:

1. Follow the existing JSON structure
2. Include metadata and clear categorization
3. Provide both questions and comprehensive answers
4. Add explanations, not just solutions
5. Include difficulty levels
6. Test for accuracy and clarity

## 📝 License

This training data is provided for educational and research purposes.

## 🔗 Integration with Main Project

This training data complements the main UMAP-inspired Universal Analogy Engine by:
- Providing diverse training examples across domains
- Enabling evaluation of semantic understanding
- Supporting multi-domain learning experiments
- Offering benchmarks for analogy-based reasoning

## 🎯 Future Enhancements

Planned additions:
- [ ] Video transcript analysis examples
- [ ] Scientific paper review training data
- [ ] Software architecture decision records
- [ ] Ethical reasoning scenarios
- [ ] Translation and localization examples
- [ ] Multi-modal examples (image + text)

## 📚 References

Each domain's training data is based on:
- Industry best practices
- Academic literature
- Professional standards
- Real-world scenarios (anonymized and fictionalized)

---

**Version**: 1.0
**Last Updated**: 2024-11-18
**Maintainer**: Claude Code Framework Team

For questions or suggestions, please open an issue or submit a pull request.
