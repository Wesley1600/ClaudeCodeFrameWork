# Sample Markdown Document

This document contains intentional issues for testing markdown validators.

## Section with Issues

This is a paragraph with some very passive voice constructions that should be detected by grammar checkers.

The code was written by the developer.  The tests were run by the CI system.

### Subsection

Here are some issues:

- List item without proper spacing
-Another list item (missing space after dash)
* Mixed list markers (should be consistent)

Code block without language specification:
```
function example() {
    return true;
}
```

Code block with language (good):
```javascript
function goodExample() {
    return true;
}
```


Multiple blank lines above (should be single)

A sentence with  multiple  spaces  between  words.

A sentence that is really, really, really, really, really, really, really, really, really long and doesn't break across multiple lines which makes it hard to read.

## Another Section

Missing blank line before this heading

Here's a [broken link](http://example-broken-link-that-does-not-exist.com/page).

Inline code without backticks: variable_name should have backticks.

Proper inline code: `variable_name`

### Formatting Issues

**Bold text with inconsistent spacing ** around it.

*Italic text *

~~Strikethrough~~

HEADINGS IN ALL CAPS (SHOULD USE TITLE CASE)

## Good Examples

Here's a properly formatted section:

- Consistent list item 1
- Consistent list item 2
- Consistent list item 3

A well-structured paragraph that follows best practices. It has proper spacing, uses active voice when possible, and maintains reasonable line length.

Code example with proper language tag:

```python
def calculate_sum(numbers):
    """Calculate the sum of a list of numbers."""
    return sum(numbers)
```

### Checklist

- [ ] Incomplete task
- [x] Completed task
- [ ] Another incomplete task

## Conclusion

This document demonstrates various markdown and prose issues that validators can detect and help fix.

---

**Note**: This is a sample document for testing purposes only.