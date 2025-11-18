# Files API Skill

A comprehensive skill for interfacing with Claude's Files API to upload, download, and manage files. This skill enables persistent file storage, intermediate output management, and file sharing through the Anthropic Files API.

## Features

- **Upload Files**: Upload documents, images, and data files to Claude's Files API
- **Download Files**: Retrieve previously uploaded files by their file ID
- **List Files**: View all uploaded files with metadata
- **Delete Files**: Remove files from storage
- **Track Metadata**: Maintain local records of uploaded files
- **Intermediate Storage**: Save and manage intermediate computation outputs
- **File Links**: Generate shareable file IDs for later retrieval

## Supported File Types

- **Documents**: PDF, DOCX, TXT, Markdown
- **Data**: CSV, Excel (XLSX, XLS), JSON
- **Images**: PNG, JPG, JPEG, GIF, WebP
- **Maximum File Size**: 350 MB per file

## API Endpoints

The skill interfaces with the following Anthropic Files API endpoints:

- `POST /v1/files` - Upload a file
- `GET /v1/files` - List all files
- `GET /v1/files/{file_id}` - Get file metadata
- `GET /v1/files/{file_id}/content` - Download file content
- `DELETE /v1/files/{file_id}` - Delete a file

## Usage

### Upload a File

```python
from files_manager import FilesManager

manager = FilesManager()
result = manager.upload_file(
    file_path="/path/to/document.pdf",
    purpose="analysis"
)
print(f"File uploaded: {result['file_id']}")
```

### Download a File

```python
content = manager.download_file(
    file_id="file_011CNha8iCJcU1wXNR6q4V8w",
    output_path="/path/to/save/document.pdf"
)
```

### List All Files

```python
files = manager.list_files()
for file in files:
    print(f"{file['filename']}: {file['file_id']}")
```

### Delete a File

```python
manager.delete_file(file_id="file_011CNha8iCJcU1wXNR6q4V8w")
```

### Store Intermediate Outputs

```python
# Save intermediate computation results
intermediate_data = {"embeddings": [...], "metadata": {...}}
file_id = manager.store_intermediate(
    data=intermediate_data,
    name="embedding_results",
    format="json"
)
```

## Configuration

The skill requires an Anthropic API key set in your environment:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

### Configuration File

The skill maintains a configuration file at `.claude/skills/files-api/config.json`:

```json
{
  "api_version": "2023-06-01",
  "beta_version": "files-api-2025-04-14",
  "storage_dir": ".claude/skills/files-api/storage",
  "tracking_db": ".claude/skills/files-api/files_db.json"
}
```

## File Tracking Database

The skill maintains a local JSON database of uploaded files:

```json
{
  "files": [
    {
      "file_id": "file_011CNha8iCJcU1wXNR6q4V8w",
      "filename": "document.pdf",
      "original_path": "/path/to/document.pdf",
      "uploaded_at": "2025-11-18T10:30:00Z",
      "size_bytes": 1024000,
      "purpose": "analysis",
      "metadata": {}
    }
  ]
}
```

## Error Handling

The skill provides comprehensive error handling:

- **Authentication Errors**: Invalid API key
- **File Not Found**: Missing local or remote files
- **Size Limit Exceeded**: Files larger than 350 MB
- **Network Errors**: Connection and timeout issues
- **API Rate Limits**: Automatic retry with exponential backoff

## Examples

### Example 1: Upload and Analyze a Document

```python
# Upload a research paper
file_id = manager.upload_file("research_paper.pdf", purpose="analysis")

# Later, download it for processing
manager.download_file(file_id, "downloaded_paper.pdf")
```

### Example 2: Store Intermediate Results

```python
# Generate embeddings
embeddings = generate_embeddings(text_corpus)

# Store for later use
file_id = manager.store_intermediate(
    data={"embeddings": embeddings, "corpus_size": len(text_corpus)},
    name="text_embeddings",
    format="json"
)

# Retrieve later
data = manager.retrieve_intermediate(file_id)
```

### Example 3: Batch File Management

```python
# Upload multiple files
file_ids = []
for file_path in document_paths:
    result = manager.upload_file(file_path)
    file_ids.append(result['file_id'])

# List and filter
all_files = manager.list_files()
pdf_files = [f for f in all_files if f['filename'].endswith('.pdf')]

# Cleanup old files
manager.cleanup_old_files(days=30)
```

## Integration with Claude Code

This skill integrates seamlessly with Claude Code workflows:

1. **Document Analysis**: Upload documents for analysis without re-uploading
2. **Data Pipeline**: Store intermediate computation results
3. **Report Generation**: Save generated reports and retrieve them later
4. **File Sharing**: Share file IDs across different Claude sessions

## API Reference

### FilesManager Class

#### `__init__(api_key=None, config_path=None)`
Initialize the Files Manager with optional API key and config path.

#### `upload_file(file_path, purpose='user', metadata=None)`
Upload a file to the Files API.

**Parameters:**
- `file_path` (str): Path to the file to upload
- `purpose` (str): Purpose of the file (default: 'user')
- `metadata` (dict): Additional metadata to store

**Returns:** dict with `file_id`, `filename`, `size_bytes`

#### `download_file(file_id, output_path=None)`
Download a file from the Files API.

**Parameters:**
- `file_id` (str): The file ID to download
- `output_path` (str): Where to save the file (optional)

**Returns:** File content as bytes or saves to output_path

#### `list_files()`
List all uploaded files.

**Returns:** List of file metadata dictionaries

#### `delete_file(file_id)`
Delete a file from the Files API.

**Parameters:**
- `file_id` (str): The file ID to delete

#### `store_intermediate(data, name, format='json')`
Store intermediate computation results.

**Parameters:**
- `data`: The data to store (dict, list, str)
- `name` (str): Name for the intermediate file
- `format` (str): Format to store in ('json', 'txt', 'csv')

**Returns:** File ID of stored data

#### `cleanup_old_files(days=30)`
Delete files older than specified days.

**Parameters:**
- `days` (int): Delete files older than this many days

## Security Considerations

- API keys are read from environment variables, never hardcoded
- File metadata is stored locally with appropriate permissions
- Sensitive data should be encrypted before upload
- Regular cleanup of old files is recommended

## Troubleshooting

### "API Key Not Found"
Set your API key: `export ANTHROPIC_API_KEY="your_key"`

### "File Too Large"
The Files API has a 350 MB limit. Split large files or compress them.

### "Network Error"
Check your internet connection and API status at status.anthropic.com

### "Permission Denied"
Ensure the storage directory has write permissions.

## Contributing

To extend this skill:
1. Add new file format handlers in `files_manager.py`
2. Implement additional metadata tracking
3. Add compression/encryption features
4. Create custom upload/download filters

## License

This skill is part of the ClaudeCodeFrameWork project.
