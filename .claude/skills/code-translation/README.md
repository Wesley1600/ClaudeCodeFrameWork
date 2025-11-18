# Code Translation Skill

A comprehensive skill for translating code from one programming language to another with automated testing and validation.

## Overview

The code translation skill helps you convert code between different programming languages while ensuring functional equivalence through automated testing. It uses LLM reasoning to perform intelligent translations and leverages code execution to validate the results.

## Features

- **Multi-language support**: Translate between popular languages (Python, JavaScript, TypeScript, Java, Go, etc.)
- **Intelligent translation**: Uses LLM reasoning to handle language-specific idioms and patterns
- **Automated testing**: Generates and runs tests for both source and translated code
- **Static analysis**: Validates syntax and types where applicable
- **Comprehensive reporting**: Provides detailed reports on translation quality and test results
- **Idiomatic output**: Produces code that follows target language best practices

## Usage

### Basic Usage

To use the skill, invoke it and provide the code you want to translate:

```
/skill code-translation

Please translate this Python function to JavaScript:
[paste your code here]
```

### Specifying Languages

You can explicitly specify source and target languages:

```
Translate this Java code to Python:
[paste your code here]
```

### Translating Files

You can also translate entire files:

```
Translate the file src/utils.py to JavaScript
```

## How It Works

1. **Analysis**: The skill analyzes your source code to understand its structure and functionality
2. **Translation**: Converts code to the target language using intelligent mapping of constructs
3. **Test Generation**: Creates test cases to verify behavioral equivalence
4. **Execution**: Runs tests on both original and translated code
5. **Validation**: Compares results and identifies any discrepancies
6. **Reporting**: Provides comprehensive output with translated code and test results

## Supported Languages

The skill supports translation between:

- Python
- JavaScript
- TypeScript
- Java
- Go
- Kotlin
- Ruby
- And other common languages

## Example Translation

**Input (Python):**
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Output (JavaScript):**
```javascript
function fibonacci(n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

## Translation Features

### Handled Patterns

- Function definitions and calls
- Class definitions and inheritance
- Type systems (dynamic ↔ static)
- Error handling
- Async/await patterns
- List/array operations
- String manipulation
- File I/O
- And more...

### Smart Conversions

- Python list comprehensions → JavaScript map/filter
- Python decorators → wrapper functions or annotations
- Python `with` statements → try/finally blocks
- Type hints → TypeScript types or JSDoc comments
- And many other language-specific patterns

## Test Execution

The skill automatically:

- Creates temporary test files
- Runs tests using appropriate frameworks (pytest, jest, etc.)
- Captures and analyzes output
- Cleans up temporary files
- Reports test results

## Output

You'll receive:

1. **Translated code**: Ready to use in your project
2. **Test results**: For both source and translated versions
3. **Translation report**: Including:
   - Key transformations applied
   - Dependencies mapped
   - Challenges encountered
   - Recommendations for deployment

## Limitations

- Some language-specific features may not have exact equivalents
- Complex metaprogramming may require manual review
- Performance characteristics may differ between languages
- Some libraries may not have equivalent versions

The skill will document any limitations or required manual review in the translation report.

## Example Session

```
User: Translate this Python code to JavaScript

def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

AI: I'll translate this Python function to JavaScript and test both versions.

[Analysis, translation, and testing process]

## Translated Code

```javascript
function greet(name, greeting = "Hello") {
    return `${greeting}, ${name}!`;
}
```

## Test Results

Source (Python): ✓ All 5 tests passed
Translated (JavaScript): ✓ All 5 tests passed

The translation is functionally equivalent and ready to use!
```

## Tips for Best Results

1. **Provide context**: Include comments and documentation
2. **Specify frameworks**: Mention if you use specific libraries
3. **Define requirements**: State any constraints or preferences
4. **Review output**: Always review translated code, especially for production use
5. **Test thoroughly**: The skill provides basic tests, but add your own for complex logic

## Files

- `code-translation.md`: The skill definition and instructions

## Contributing

To enhance this skill:

1. Edit `.claude/skills/code-translation.md`
2. Add support for new language pairs
3. Improve translation patterns
4. Enhance test generation

---

**Note**: This skill is designed to assist with code translation, but human review is always recommended for production code.
