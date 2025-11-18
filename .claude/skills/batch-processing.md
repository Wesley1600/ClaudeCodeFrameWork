# Batch Processing Skill

You are now in batch processing mode. Your task is to efficiently process multiple similar tasks in a single operation, reducing overhead and maintaining consistent processing.

## Core Principles

1. **Efficiency First**: Process tasks in parallel when safe, sequentially when dependencies exist
2. **Consistency**: Apply the same logic/transformations to all items in the batch
3. **Error Handling**: Continue processing remaining items even if some fail, report all errors at the end
4. **Progress Tracking**: Use TodoWrite to track progress through the batch
5. **Resource Management**: Be mindful of memory and computational limits

## Supported Batch Operations

### 1. File Processing
- **PDF Processing**: Extract text, convert formats, merge/split, apply transformations
- **Image Processing**: Resize, convert, compress, apply filters
- **Text Files**: Parse, transform, extract data, generate reports
- **Code Files**: Analyze, refactor, apply fixes, run linters
- **Data Files**: Process JSON, CSV, XML files in bulk

### 2. Script Execution
- **Test Suites**: Run multiple test files or test cases
- **Build Scripts**: Execute builds for multiple packages/modules
- **Data Processing**: Run analytics or transformations on multiple datasets
- **API Calls**: Make multiple similar API requests
- **Automation Scripts**: Execute similar automation tasks

### 3. Code Operations
- **Refactoring**: Apply same refactoring pattern across multiple files
- **Code Generation**: Generate similar components/modules
- **Linting/Formatting**: Apply to multiple files
- **Migration**: Update code across multiple files
- **Bug Fixes**: Apply similar fixes across multiple locations

## Batch Processing Workflow

### Phase 1: Understanding & Planning
1. **Identify the task type and scope**: What operation needs to be performed on how many items?
2. **Determine processing strategy**: Can tasks run in parallel or must they be sequential?
3. **Identify failure modes**: What could go wrong? How to handle errors?
4. **Create TodoWrite list**: Track all batch items for visibility
5. **Estimate resources**: Check if batch size is reasonable for available resources

### Phase 2: Validation
1. **Verify inputs exist**: Check all files/scripts are accessible
2. **Check prerequisites**: Ensure dependencies are installed/available
3. **Validate parameters**: Ensure task parameters are consistent and valid
4. **Risk assessment**: Warn about potential issues before processing
5. **Create backup plan**: For destructive operations, ensure backups exist

### Phase 3: Execution
1. **Process efficiently**: Use parallel processing when safe, sequential when necessary
2. **Track progress**: Update TodoWrite after each item or batch of items
3. **Capture outputs**: Collect all results, errors, and warnings
4. **Error resilience**: Continue processing even if individual items fail
5. **Resource monitoring**: Be mindful of memory/CPU usage for large batches

### Phase 4: Reporting
1. **Summary statistics**: Total items, succeeded, failed, skipped
2. **Success details**: Key outcomes for successful items
3. **Failure details**: Detailed error information for failed items
4. **Recommendations**: Suggest fixes or next steps
5. **Artifacts**: List any generated files or outputs

## Processing Strategies

### Parallel Processing
**Use when:**
- Tasks are independent with no shared state
- Order doesn't matter
- No race conditions possible
- Examples: Reading files, running independent tests, processing images

**Implementation:**
- Make multiple tool calls in a single message
- Example: Reading 5 files simultaneously using 5 Read tool calls
- Reduces latency and improves throughput

### Sequential Processing
**Use when:**
- Tasks have dependencies on previous results
- Order matters
- Shared state needs to be modified
- Resource constraints require throttling
- Examples: Chained transformations, cumulative operations

**Implementation:**
- Process one item at a time
- Update TodoWrite after each item
- Use results from previous item to inform next one

### Hybrid Processing
**Use when:**
- Can process in batches but not all at once
- Need to balance parallelism with resource limits
- Example: Process 10 files at a time from a set of 100

**Implementation:**
- Divide total set into smaller batches
- Process each batch in parallel
- Process batches sequentially

## Error Handling Strategy

1. **Continue on Error**: Don't stop entire batch if one item fails
2. **Collect All Errors**: Gather error details for all failed items
3. **Categorize Failures**: Group by error type for easier debugging
4. **Provide Context**: Include item identifier and error details
5. **Suggest Fixes**: Recommend solutions for common errors
6. **Partial Success**: Clearly report which items succeeded vs failed

## Best Practices

### Before Processing
- Validate all inputs exist and are accessible
- Check file permissions for read/write operations
- Estimate total processing time
- Warn if batch size is very large (>100 items)
- Create backups for destructive operations

### During Processing
- Update TodoWrite regularly to show progress
- Use parallel processing when safe to do so
- Implement proper error handling
- Monitor resource usage
- Log important events and errors

### After Processing
- Provide comprehensive summary report
- List all successes and failures
- Include relevant statistics
- Suggest next steps or fixes
- Clean up temporary files if any

## Common Batch Operations

### Batch File Processing
When asked to process multiple files:
1. Use Glob to find all matching files
2. Create TodoWrite entry for each file
3. Validate all files exist and are readable
4. Process in parallel using multiple Read/Edit/Write calls
5. Report results with statistics

### Batch Script Execution
When asked to run multiple scripts:
1. Verify all scripts exist and are executable
2. Determine if scripts can run in parallel
3. Create TodoWrite entry for each script
4. Execute using Bash tool (parallel or sequential)
5. Capture all outputs and exit codes
6. Report successes and failures

### Batch Code Refactoring
When asked to refactor code across multiple files:
1. Use Grep to find all locations needing changes
2. Read all affected files
3. Create TodoWrite entry for each file
4. Apply transformations consistently
5. Verify changes don't break syntax
6. Report all changes made

### Batch Data Processing
When asked to process multiple data files:
1. Identify data format (JSON, CSV, XML, etc.)
2. Read and parse all files
3. Apply same transformation/analysis to each
4. Handle parsing errors gracefully
5. Generate aggregate reports if needed
6. Save results in consistent format

## Example Invocations

When user requests batch processing, they might say:
- "Process all PDF files in the documents folder and extract text"
- "Run all test files in the tests directory"
- "Convert all PNG images to JPEG format"
- "Apply the same refactoring to all component files"
- "Execute all Python scripts in the scripts folder"
- "Parse all JSON files and generate a summary report"

## Response Template

For each batch operation, structure your response as:

1. **Understanding**: Confirm what batch operation is requested
2. **Planning**: Create TodoWrite list of all items
3. **Validation**: Check prerequisites and inputs
4. **Execution**: Process items efficiently
5. **Reporting**: Provide comprehensive summary

Example summary format:
```
Batch Processing Complete
========================
Total Items: 25
✓ Succeeded: 23
✗ Failed: 2
⊘ Skipped: 0

Successes:
- file1.txt: Processed successfully (125 lines)
- file2.txt: Processed successfully (89 lines)
[... more ...]

Failures:
- file24.txt: Permission denied
- file25.txt: Invalid format

Recommendations:
- Fix permissions on file24.txt using chmod
- Validate and fix format in file25.txt
```

## Integration with Other Skills

This batch processing skill can be combined with:
- PDF processing skills for batch PDF operations
- Image processing for batch image operations
- Code analysis for batch code reviews
- Testing frameworks for batch test execution
- Data analysis for batch data processing

## Performance Considerations

- For batches >50 items, consider processing in chunks
- For file operations, be mindful of file sizes
- For network operations, implement rate limiting
- For CPU-intensive tasks, consider sequential processing
- Monitor memory usage for large data processing

## Safety Checks

Before processing batch operations:
- Confirm destructive operations with user
- Verify backup exists for data modification
- Check available disk space for output generation
- Validate file paths to prevent path traversal
- Ensure operations won't exceed resource limits

---

You are now ready to efficiently process batch operations. Always prioritize:
1. User's goal and requirements
2. Efficiency through appropriate parallelization
3. Robustness through error handling
4. Transparency through progress tracking
5. Completeness through comprehensive reporting
