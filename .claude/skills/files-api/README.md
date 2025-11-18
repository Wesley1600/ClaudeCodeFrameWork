# Files API Skill

A comprehensive skill for interfacing with Claude's Files API to upload, download, and manage files.

## Quick Start

### 1. Set up your API key

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

### 2. Install dependencies

```bash
pip install requests
```

### 3. Basic Usage

```python
from files_manager import FilesManager

# Initialize manager
manager = FilesManager()

# Upload a file
result = manager.upload_file("document.pdf")
print(f"File ID: {result['file_id']}")

# Download a file
manager.download_file(file_id, "output.pdf")

# List all files
files = manager.list_files()
for f in files:
    print(f"{f['filename']}: {f['file_id']}")
```

## Examples

Run the examples script to see all features in action:

```bash
cd .claude/skills/files-api
python examples.py
```

This will demonstrate:
- ✅ Basic upload and download
- ✅ Storing intermediate computation results
- ✅ Listing and searching files
- ✅ Storage statistics
- ✅ Batch operations
- ✅ Error handling

## Features

### File Management
- Upload files up to 350 MB
- Download files by ID
- List all uploaded files
- Delete files
- Search files by name, purpose, or metadata

### Intermediate Storage
- Store computation results (JSON, TXT, CSV)
- Retrieve intermediate data
- Track processing pipelines

### Advanced Features
- Automatic retry with exponential backoff
- File metadata tracking
- Storage statistics
- Cleanup old files
- Batch operations

## File Structure

```
.claude/skills/files-api/
├── skill.md              # Skill documentation
├── files_manager.py      # Main implementation
├── examples.py           # Usage examples
├── config.json           # Configuration
├── files_db.json         # File tracking database (auto-generated)
├── storage/              # Local storage directory (auto-generated)
└── README.md            # This file
```

## API Reference

### FilesManager

#### Constructor
```python
manager = FilesManager(api_key=None, config_path=None)
```

#### Methods

**upload_file(file_path, purpose='user', metadata=None)**
- Upload a file to the Files API
- Returns: `{'file_id': str, 'filename': str, 'size_bytes': int}`

**download_file(file_id, output_path=None)**
- Download a file from the Files API
- Returns: bytes or Path (if output_path provided)

**list_files()**
- List all uploaded files
- Returns: List of file metadata dicts

**delete_file(file_id)**
- Delete a file
- Returns: bool

**store_intermediate(data, name, format='json')**
- Store intermediate results
- Returns: file_id

**retrieve_intermediate(file_id)**
- Retrieve intermediate results
- Returns: Parsed data

**search_files(filename=None, purpose=None, metadata_filter=None)**
- Search files by criteria
- Returns: List of matching files

**get_storage_stats()**
- Get storage statistics
- Returns: Dict with stats

**cleanup_old_files(days=30)**
- Delete files older than N days
- Returns: Number of files deleted

## Configuration

Edit `config.json` to customize:

```json
{
  "api_version": "2023-06-01",
  "beta_version": "files-api-2025-04-14",
  "storage_dir": ".claude/skills/files-api/storage",
  "tracking_db": ".claude/skills/files-api/files_db.json",
  "max_file_size_mb": 350,
  "auto_cleanup_days": 30,
  "retry_attempts": 4
}
```

## Error Handling

The skill provides specific exceptions:

- `AuthenticationError` - Invalid API key
- `FileNotFoundError` - File doesn't exist
- `FileSizeLimitError` - File exceeds 350 MB limit
- `FilesAPIError` - General API errors

## Use Cases

### 1. Document Analysis Pipeline

```python
# Upload document once
file_id = manager.upload_file("research_paper.pdf")

# Use in multiple analysis steps without re-uploading
# File ID can be referenced in API calls
```

### 2. Machine Learning Workflow

```python
# Store training results
results = {"model": "UMAP", "accuracy": 0.95, "embeddings": [...]}
file_id = manager.store_intermediate(results, "training_results")

# Later, retrieve for evaluation
data = manager.retrieve_intermediate(file_id)
```

### 3. Batch Processing

```python
# Upload batch of files
file_ids = []
for doc in documents:
    result = manager.upload_file(doc, metadata={"batch": "2025-11"})
    file_ids.append(result['file_id'])

# Process all
for file_id in file_ids:
    content = manager.download_file(file_id)
    process(content)
```

## Troubleshooting

### API Key Error
```
AuthenticationError: API key not found
```
**Solution:** Set `ANTHROPIC_API_KEY` environment variable

### File Too Large
```
FileSizeLimitError: File size exceeds limit
```
**Solution:** Files must be under 350 MB. Compress or split the file.

### Network Issues
```
FilesAPIError: Request failed after 4 attempts
```
**Solution:** Check internet connection. The skill auto-retries with exponential backoff.

### Permission Denied
```
PermissionError: [Errno 13] Permission denied
```
**Solution:** Ensure write permissions for `.claude/skills/files-api/storage/`

## Integration with Claude Code

This skill integrates seamlessly with Claude Code workflows:

1. **Invoke the skill**: Use the Skill tool in Claude Code
2. **Use in conversations**: Reference file IDs in prompts
3. **Automate workflows**: Combine with other skills for complex tasks

## Security

- API keys are read from environment variables only
- File metadata stored locally with appropriate permissions
- Sensitive data should be encrypted before upload
- Regular cleanup recommended for security and storage management

## Contributing

To extend this skill:

1. Add new methods to `FilesManager` class
2. Update `skill.md` documentation
3. Add examples to `examples.py`
4. Test thoroughly before committing

## License

Part of the ClaudeCodeFrameWork project.

## Support

For issues or questions:
- Check the [skill.md](skill.md) documentation
- Review [examples.py](examples.py) for usage patterns
- Consult the [Anthropic Files API docs](https://docs.claude.com/en/api/files-content)
