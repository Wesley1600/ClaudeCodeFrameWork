# Activity Logging System

Comprehensive activity logging and reporting system for the UMAP Analogy Engine, providing transparency and auditability of agent activities.

## Overview

The activity logging system consists of three main components:

1. **ActivityLogger** (`activity_logger.py`) - Core logging functionality with file-based persistence
2. **ReportGenerator** (`report_generator.py`) - Summary report generation (daily and per-task)
3. **LoggedUMAPEngine** (`logged_umap_wrapper.py`) - Wrapper for UMAP engine with integrated logging

## Features

- **Structured Logging**: JSON-based logs (JSONL format) for easy parsing and analysis
- **Activity Categorization**: TRAINING, INFERENCE, CONFIG, SYSTEM, MODEL, DATA
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Thread-Safe**: Safe for concurrent logging operations
- **Automatic Timestamping**: ISO 8601 timestamps for all events
- **Session Management**: Each run gets a unique session ID
- **Report Generation**: Markdown and JSON summary reports
- **Transparency**: Complete audit trail of all agent activities

## Quick Start

### Basic Usage with LoggedUMAPEngine

```python
from logged_umap_wrapper import LoggedUMAPEngine
import torch

# Create logged engine
engine = LoggedUMAPEngine(
    task_name="my_experiment",
    enable_logging=True,
    enable_console=True
)

# Train with automatic logging
model, embeddings = engine.train(
    X=data,
    pair_indices_list=relations,
    relation_names=["capital", "gender"],
    epochs=200
)

# Query with logging
results = engine.find_analogy(
    model=model,
    X=data,
    query_idx=10,
    relation_idx=0,
    pair_indices_list=relations,
    k=5
)

# Close session and generate report
report_path = engine.close_and_report(generate_report=True)
print(f"Report saved to: {report_path}")
```

### Manual Logging for Custom Activities

```python
from activity_logger import ActivityLogger, ActivityType, LogLevel

# Create logger
logger = ActivityLogger(
    task_name="custom_task",
    enable_console=True
)

# Log configuration
logger.log_config(
    config_name="hyperparameters",
    config_values={
        "learning_rate": 1e-3,
        "batch_size": 128,
        "epochs": 100
    }
)

# Log custom activity
logger.log_activity(
    activity_type=ActivityType.TRAINING,
    message="Starting hyperparameter search",
    level=LogLevel.INFO,
    metadata={"search_space_size": 100}
)

# Log training epoch
logger.log_training_epoch(
    epoch=10,
    total_epochs=100,
    losses={"total": 0.5, "umap": 0.3, "align": 0.2}
)

# Log errors
logger.log_error(
    error_message="CUDA out of memory",
    metadata={"batch_size": 128, "memory_gb": 8}
)

# Close session
logger.close_session(summary={"best_loss": 0.123})
```

## Log File Structure

Logs are stored in JSONL format (one JSON object per line) in `memory/logs/`.

### Filename Format
```
{YYYYMMDD}_{HHMMSS}_{task_name}.jsonl
```

Example: `20251118_143000_word_analogies.jsonl`

### Log Entry Format

```json
{
  "log_type": "ACTIVITY",
  "timestamp": "2025-11-18T14:30:00.123456",
  "session_id": "20251118_143000",
  "task_name": "word_analogies",
  "activity_type": "TRAINING",
  "level": "INFO",
  "message": "Epoch 10/200 - Loss: 0.543210",
  "metadata": {
    "epoch": 10,
    "total_epochs": 200,
    "losses": {
      "total": 0.54321,
      "umap": 0.32145,
      "align": 0.22176
    }
  }
}
```

## Report Generation

### Generate Reports Programmatically

```python
from report_generator import ReportGenerator

generator = ReportGenerator()

# Daily report
generator.generate_daily_report(
    date="20251118",
    output_format="markdown"  # or "json"
)

# Session report
generator.generate_session_report(
    session_id="20251118_143000",
    output_format="markdown"
)

# Training summary
generator.generate_training_summary(
    session_id="20251118_143000",
    output_format="markdown"
)
```

### Generate All Reports for Today

```python
from report_generator import generate_all_reports

generate_all_reports()  # Uses today's date
generate_all_reports(date="20251118")  # Specific date
```

## Report Types

### Daily Report
- Summary of all activities for a specific day
- Lists all sessions and tasks
- Aggregates errors and warnings
- Breakdown by activity type and log level

**Location**: `memory/reports/daily_report_{YYYYMMDD}.md`

### Session Report
- Detailed view of a single session
- Start/end time and duration
- Activity and log level breakdowns
- All errors and warnings

**Location**: `memory/reports/session_report_{session_id}.md`

### Training Summary
- Focused on training activities
- Loss history and components
- Best/final/average losses
- Epoch-by-epoch statistics

**Location**: `memory/reports/training_summary_{session_id}.md`

## Reading Logs Programmatically

```python
from activity_logger import LogReader, ActivityType, LogLevel

reader = LogReader()

# Read specific session
logs = reader.read_session("20251118_143000")

# Read all logs from a date
logs = reader.read_logs_by_date("20251118")

# Read all logs
all_logs = reader.read_all_logs()

# Filter by activity type
training_logs = reader.filter_by_type(logs, ActivityType.TRAINING)
inference_logs = reader.filter_by_type(logs, ActivityType.INFERENCE)

# Filter by log level
errors = reader.filter_by_level(logs, LogLevel.ERROR)
warnings = reader.filter_by_level(logs, LogLevel.WARNING)

# List all sessions
sessions = reader.get_sessions()
```

## Activity Types

- **TRAINING**: Model training activities (epochs, losses, metrics)
- **INFERENCE**: Inference/analogy queries and results
- **CONFIG**: Configuration changes and hyperparameter settings
- **SYSTEM**: System events (initialization, warnings, errors)
- **MODEL**: Model-related operations (loading, saving, extraction)
- **DATA**: Data processing activities

## Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages for failures

## Directory Structure

```
memory/
├── logs/                          # Activity log files
│   ├── 20251118_143000_task1.jsonl
│   ├── 20251118_150000_task2.jsonl
│   └── ...
└── reports/                       # Generated reports
    ├── daily_report_20251118.md
    ├── daily_report_20251118.json
    ├── session_report_20251118_143000.md
    ├── training_summary_20251118_143000.md
    └── ...
```

## Examples

### Example 1: Basic Logging
```bash
python test_logging_basic.py
```

Tests core logging functionality without requiring full UMAP training.

### Example 2: Full Training with Logging
```bash
python example_logged_training.py
```

Demonstrates complete workflow:
- Training with activity logging
- Inference queries with logging
- Custom activity logging
- Report generation

## Best Practices

1. **Task Naming**: Use descriptive task names (e.g., "word_analogies_experiment_v2")
2. **Metadata**: Include relevant metadata for auditability
3. **Log Levels**: Use appropriate log levels (don't log everything as ERROR)
4. **Session Management**: Always close sessions with `close_session()`
5. **Report Generation**: Generate reports after experiments for documentation
6. **Error Logging**: Log exceptions with context for debugging

## API Reference

### ActivityLogger

```python
ActivityLogger(
    task_name: str = "default",
    log_dir: str = "memory/logs",
    enable_console: bool = True,
    min_level: LogLevel = LogLevel.INFO
)
```

**Methods**:
- `log_activity(activity_type, message, level, metadata)` - Log general activity
- `log_training_epoch(epoch, total_epochs, losses, metrics)` - Log training epoch
- `log_inference(query, result, method, metadata)` - Log inference query
- `log_config(config_name, config_values)` - Log configuration
- `log_error(error_message, exception, metadata)` - Log error
- `log_model_info(model_name, parameters, metadata)` - Log model info
- `close_session(summary)` - Close logging session

### LoggedUMAPEngine

```python
LoggedUMAPEngine(
    task_name: str = "umap_analogy",
    enable_logging: bool = True,
    enable_console: bool = True,
    log_level: LogLevel = LogLevel.INFO
)
```

**Methods**:
- `train(X, pair_indices_list, relation_names, **kwargs)` - Train with logging
- `find_analogy(model, X, query_idx, relation_idx, ...)` - Find analogy with logging
- `analogy_from_pair(model, X, ref_a, ref_b, query_idx, ...)` - Analogy from pair
- `extract_relations(embeddings, pair_indices_list, relation_names)` - Extract relations
- `close_and_report(generate_report)` - Close session and generate report
- `get_session_id()` - Get current session ID
- `get_log_file()` - Get log file path

### ReportGenerator

```python
ReportGenerator(
    log_dir: str = "memory/logs",
    report_dir: str = "memory/reports"
)
```

**Methods**:
- `generate_daily_report(date, output_format)` - Generate daily report
- `generate_session_report(session_id, output_format)` - Generate session report
- `generate_training_summary(session_id, output_format)` - Generate training summary
- `list_available_sessions()` - List all session IDs
- `list_available_reports()` - List all generated reports

## Integration with Existing Code

The logging system is designed as a non-invasive wrapper. To add logging to existing code:

**Before**:
```python
from umap_analogy_engine import train_relation_aware_umap

model, embeddings = train_relation_aware_umap(X, pairs, names)
```

**After**:
```python
from logged_umap_wrapper import LoggedUMAPEngine

engine = LoggedUMAPEngine(task_name="my_experiment")
model, embeddings = engine.train(X, pairs, names)
engine.close_and_report()
```

All parameters are passed through to the original functions, so no changes to your existing configurations are needed.

## Transparency and Auditability

The logging system provides:

1. **Complete Audit Trail**: Every action is logged with timestamps
2. **Reproducibility**: Configuration and hyperparameters are logged
3. **Debugging**: Errors and warnings with full context
4. **Performance Tracking**: Training metrics and inference times
5. **Accountability**: Session-based tracking of all activities
6. **Reporting**: Automatic summary generation for documentation

## Troubleshooting

### Logs not being created
- Check that `memory/logs/` directory exists
- Verify file permissions
- Ensure `enable_logging=True`

### Reports not generating
- Verify log files exist in `memory/logs/`
- Check that session ID matches log filename
- Ensure `memory/reports/` directory exists

### Missing activities in logs
- Check `min_level` setting (may be filtering out DEBUG/INFO)
- Verify `enable_logging=True`
- Ensure `log_activity()` is being called

## License

Same as the main UMAP Analogy Engine project.

## Support

For issues or questions about the activity logging system, please refer to the example scripts or open an issue in the project repository.
