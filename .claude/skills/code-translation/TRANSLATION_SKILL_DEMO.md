# Code Translation Skill - Demo Guide

This document demonstrates how to use the code translation skill to translate code between programming languages.

## Quick Start

### 1. Activate the Skill

To use the code translation skill, invoke it with:

```
/skill code-translation
```

Then provide your translation request.

### 2. Example Translations

#### Example 1: Simple Function (Python → JavaScript)

**Input:**
```
Translate this Python function to JavaScript:

def add_numbers(a, b):
    """Add two numbers and return the result."""
    return a + b
```

**Expected Output:**
- Translated JavaScript function
- Test results for both Python and JavaScript versions
- Detailed translation report

#### Example 2: Class Translation (Python → Java)

**Input:**
```
Translate this Python class to Java:

class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, value):
        self.result += value
        return self.result

    def reset(self):
        self.result = 0
```

**Expected Output:**
- Java class with equivalent functionality
- Proper Java conventions (getters/setters if appropriate)
- Test results

#### Example 3: Using the Test Example File

We've included a test file `test_translation_example.py` with string utility functions:

```
Translate test_translation_example.py from Python to JavaScript
```

This will translate the entire file including:
- `reverse_string()` function
- `is_palindrome()` function
- `count_vowels()` function
- Associated tests

## What the Skill Does

### Analysis Phase
1. Reads and understands the source code
2. Identifies functions, classes, and data structures
3. Notes language-specific features
4. Extracts existing tests

### Translation Phase
1. Maps source constructs to target language equivalents
2. Handles special patterns:
   - List comprehensions → map/filter
   - Decorators → wrapper functions
   - Type systems
   - Error handling
   - Async patterns
3. Produces idiomatic target language code

### Testing Phase
1. Generates comprehensive test cases
2. Creates test files for both languages
3. Executes tests using appropriate frameworks
4. Compares results

### Reporting Phase
Provides a detailed report including:
- Translation summary
- Key transformations
- Test results (source and target)
- Behavioral equivalence analysis
- Recommendations

## Supported Language Pairs

### Common Translations

- **Python ↔ JavaScript**: Web backends, scripting
- **Python ↔ TypeScript**: Type-safe web development
- **Java ↔ Python**: Enterprise to scripting
- **JavaScript ↔ TypeScript**: Adding type safety
- **Python ↔ Go**: Concurrent applications
- **Java ↔ Kotlin**: Android development

## Advanced Usage

### Specifying Test Framework

```
Translate this Python code to JavaScript and use Jest for testing:
[code here]
```

### Preserving Documentation

```
Translate this Python module to TypeScript, preserving all docstrings as JSDoc comments:
[code here]
```

### Handling Dependencies

```
Translate this Python code that uses numpy to JavaScript.
Suggest equivalent libraries:
[code here]
```

## Example Output Structure

When you run a translation, you'll get:

```markdown
## Code Translation Report

### Summary
- Source Language: Python
- Target Language: JavaScript
- Translation Status: ✓ Success
- Tests Passed: 12/12

### Translated Code
[Complete, ready-to-use code]

### Test Results

#### Source Code Tests
- Status: ✓ All passed
- Tests run: 12
- Tests passed: 12

#### Translated Code Tests
- Status: ✓ All passed
- Tests run: 12
- Tests passed: 12

### Behavioral Equivalence
✓ The translated code behaves identically to the source

### Recommendations
- Install dependencies: [list]
- Review areas: [any manual checks needed]
```

## Best Practices

### 1. Start Small
Begin with simple functions before translating entire modules.

### 2. Review Output
Always review translated code, especially:
- Error handling
- Type conversions
- Edge cases
- Performance implications

### 3. Add More Tests
The skill generates basic tests, but you should add:
- Integration tests
- Performance tests
- Domain-specific tests

### 4. Check Dependencies
Verify that equivalent libraries exist in the target ecosystem.

### 5. Understand Limitations
Some features may not translate perfectly:
- Metaprogramming
- Language-specific optimizations
- Platform-specific APIs

## Testing the Translation Skill

To verify the skill is working correctly, try translating the included example:

```bash
# First, verify the Python version works
python3 test_translation_example.py

# Then use the skill to translate it
# In Claude Code:
/skill code-translation
Translate test_translation_example.py from Python to JavaScript
```

You should see:
1. Analysis of the Python code
2. JavaScript translation of all functions
3. Test generation and execution for both versions
4. Comprehensive report

## Troubleshooting

### Skill Not Found
If the skill isn't recognized:
1. Check that `.claude/skills/code-translation.md` exists
2. Restart Claude Code if necessary

### Tests Fail
If tests fail during translation:
1. Check the skill's error messages
2. The skill will attempt to fix and retry
3. Review the report for manual fixes needed

### Missing Dependencies
If a language runtime is missing:
1. Install the required language (e.g., `node`, `python3`, `java`)
2. Install testing frameworks if needed
3. Re-run the translation

## Extending the Skill

You can customize the skill by editing `.claude/skills/code-translation.md`:

- Add new language pairs
- Improve translation patterns
- Enhance test generation
- Add static analysis tools

## Real-World Use Cases

### 1. Migration Projects
Migrating a Python codebase to Node.js:
```
Translate each module systematically
Verify tests pass
Update imports and dependencies
```

### 2. Polyglot Development
Working in multiple languages:
```
Prototype in Python
Translate to Go for production
Maintain behavioral parity
```

### 3. Learning
Understanding language differences:
```
Translate familiar code to a new language
See how patterns map across languages
Learn idiomatic approaches
```

### 4. Code Review
Comparing implementations:
```
Translate to see alternative approaches
Identify optimization opportunities
```

## Performance Considerations

The skill focuses on functional correctness. After translation:

1. **Profile** the translated code
2. **Optimize** bottlenecks using language-specific techniques
3. **Benchmark** against the original if performance is critical
4. **Refactor** to use efficient data structures for the target language

## Next Steps

1. Try translating `test_translation_example.py`
2. Experiment with your own code
3. Review the translation reports
4. Provide feedback for improvements

---

**Happy Translating!** 🚀
