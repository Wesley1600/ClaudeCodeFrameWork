# Agent Pulse Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [CLI Reference](#cli-reference)
8. [Advanced Topics](#advanced-topics)
9. [Troubleshooting](#troubleshooting)

## Overview

**Agent Pulse** is a proactive AI assistant system inspired by ChatGPT Pro's Pulse feature. It transforms reactive AI assistance into proactive support by:

- Analyzing past conversations to understand context
- Conducting research on topics relevant to you
- Identifying opportunities and suggesting solutions
- Delivering personalized updates at scheduled times
- Learning from your feedback to improve over time

### Key Features

- 📊 **Conversation Analysis** - Extracts insights from past interactions
- 🔍 **Proactive Research** - Researches topics while you work
- 💡 **Opportunity Finding** - Identifies learning and improvement opportunities
- 🔧 **Problem Solving** - Suggests solutions to recurring issues
- ✅ **Action Tracking** - Monitors commitments and tasks
- 🎯 **Personalization** - Learns from feedback to tailor updates
- ⏰ **Scheduling** - Runs automatically at your preferred time

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- No external dependencies required (uses Python standard library)

### Setup

The Agent Pulse system is already included in the ClaudeCodeFrameWork. No additional installation needed!

```bash
# Navigate to the framework directory
cd ClaudeCodeFrameWork

# Verify installation
python -m agent_pulse.cli.pulse_cli --help
```

### Initial Configuration

```bash
# Set up your interests
python -m agent_pulse.cli.pulse_cli config --add-interest "machine learning"
python -m agent_pulse.cli.pulse_cli config --add-interest "python"

# Configure schedule
python -m agent_pulse.cli.pulse_cli config --set schedule_time=06:00
python -m agent_pulse.cli.pulse_cli config --set schedule_frequency=daily

# View configuration
python -m agent_pulse.cli.pulse_cli config --show
```

## Quick Start

### 1. Add a Conversation

```python
from agent_pulse import PulseOrchestrator

orchestrator = PulseOrchestrator()

# Add a conversation
conversation = orchestrator.add_conversation([
    {"role": "user", "content": "I'm working on a ML project"},
    {"role": "assistant", "content": "Great! Tell me more about it"},
    {"role": "user", "content": "Building a recommendation system"},
])
```

### 2. Generate Pulse Update

```bash
# Generate and display
python -m agent_pulse.cli.pulse_cli generate

# Save to file
python -m agent_pulse.cli.pulse_cli generate -o pulse.md
```

### 3. Provide Feedback

```bash
# Give positive feedback
python -m agent_pulse.cli.pulse_cli feedback <card_id> up

# Dismiss irrelevant cards
python -m agent_pulse.cli.pulse_cli feedback <card_id> dismiss
```

## Core Concepts

### Update Cards

Agent Pulse generates different types of update cards:

| Card Type | Purpose | Priority |
|-----------|---------|----------|
| 🔍 Research | Latest developments on topics | Medium |
| 🔧 Problem Solution | Suggested fixes for issues | High |
| 💡 Opportunity | Learning & improvement ideas | Medium |
| ✅ Action Items | Pending tasks & commitments | High |
| 📊 Metrics | Progress on tracked metrics | Medium |
| 📰 News | Recent updates in your field | Low |

### Agents

Four specialized agents work together:

1. **Conversation Analyzer** - Extracts topics, entities, problems, opportunities
2. **Research Agent** - Conducts research on trending topics
3. **Opportunity Finder** - Identifies learning and optimization opportunities
4. **Problem Solver** - Analyzes issues and suggests solutions

### Memory Store

Conversations are stored and indexed by:
- Timestamp
- Topics
- Entities (people, projects, tools)
- Action items
- Problems
- Opportunities

### Preferences

The system learns from feedback:
- **Topic weights** - Boost or reduce topics based on engagement
- **Category weights** - Prioritize card types you interact with
- **Favorites** - Topics you've marked as important
- **Dismissed** - Topics to filter out

## Usage Guide

### Python API

#### Basic Usage

```python
from agent_pulse import PulseOrchestrator, PulseConfig

# Create orchestrator
orchestrator = PulseOrchestrator()

# Add conversations
orchestrator.add_conversation([
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
])

# Generate update
pulse_update = orchestrator.generate_pulse_update()

# Render as markdown
markdown = orchestrator.render_pulse_update(pulse_update)
print(markdown)
```

#### Custom Configuration

```python
from datetime import time

config = PulseConfig()
config.user_interests = ["AI", "Python", "Web Dev"]
config.schedule_time = time(6, 0)
config.lookback_days = 14
config.max_topics_per_update = 10
config.card_style = "detailed"  # or "minimal", "comprehensive"

orchestrator = PulseOrchestrator(config)
```

#### Using the Scheduler

```python
# Set callback for scheduled runs
orchestrator.start_scheduler()

# Run immediately
orchestrator.scheduler.run_now()

# Stop scheduler
orchestrator.stop_scheduler()
```

#### Recording Feedback

```python
orchestrator.record_feedback(
    card_id="abc123...",
    feedback_type="thumbs_up",
    notes="Very helpful!"
)
```

### CLI Usage

#### Generate Updates

```bash
# Generate and display
pulse generate

# Save to file
pulse generate -o daily_update.md

# JSON output
pulse generate -o update.json -f json
```

#### Configuration

```bash
# View configuration
pulse config --show

# Set values
pulse config --set schedule_time=07:00
pulse config --set lookback_days=14
pulse config --set max_topics_per_update=8

# Manage interests
pulse config --add-interest "machine learning"
pulse config --remove-interest "old topic"
```

#### Conversation Management

```bash
# Add from file
pulse add -f conversation.json

# Add from stdin
cat conversation.json | pulse add
```

#### Feedback

```bash
# Positive feedback
pulse feedback <card_id> up

# Negative feedback
pulse feedback <card_id> down -n "Not relevant"

# Save for later
pulse feedback <card_id> save

# Dismiss
pulse feedback <card_id> dismiss
```

#### Scheduler

```bash
# Start scheduler (runs in foreground)
pulse scheduler start

# Run immediately
pulse scheduler run

# Check status
pulse scheduler status
```

#### History

```bash
# View recent updates
pulse history

# Show more entries
pulse history -c 20

# Verbose output
pulse history -v
```

#### System Status

```bash
pulse status
```

## API Reference

### PulseOrchestrator

Main class for coordinating pulse updates.

```python
class PulseOrchestrator:
    def __init__(self, config: Optional[PulseConfig] = None)
    def add_conversation(self, messages: List[Dict], metadata: Optional[Dict] = None) -> ConversationEntry
    def generate_pulse_update(self) -> Dict[str, Any]
    def render_pulse_update(self, pulse_update: Optional[Dict] = None, output_format: str = "markdown") -> str
    def record_feedback(self, card_id: str, feedback_type: str, notes: Optional[str] = None) -> None
    def start_scheduler(self) -> None
    def stop_scheduler(self) -> None
    def get_status(self) -> Dict[str, Any]
    def get_pulse_history(self, count: int = 10) -> List[Dict[str, Any]]
```

### PulseConfig

Configuration management.

```python
class PulseConfig:
    # Paths
    memory_store_path: Path
    preferences_path: Path
    conversation_history_path: Path

    # Scheduling
    schedule_enabled: bool = True
    schedule_time: time = time(6, 0)
    schedule_frequency: str = "daily"  # daily, weekly, manual

    # Analysis
    max_conversations_to_analyze: int = 50
    lookback_days: int = 7
    min_conversation_length: int = 3

    # Agents
    enable_conversation_analysis: bool = True
    enable_research: bool = True
    enable_opportunity_finding: bool = True
    enable_problem_solving: bool = True

    # Updates
    max_web_searches: int = 5
    max_topics_per_update: int = 8
    card_style: str = "detailed"  # minimal, detailed, comprehensive
    include_sources: bool = True
    include_action_items: bool = True

    # Personalization
    user_interests: List[str]
    tracked_metrics: List[str]
    focus_areas: List[str]
```

### ConversationAnalyzer

Analyzes conversations to extract insights.

```python
class ConversationAnalyzer:
    def analyze_conversation(self, conversation: ConversationEntry) -> Dict[str, Any]
    def analyze_recent_conversations(self, days: int = 7, max_count: int = 50) -> Dict[str, Any]
    def get_trending_topics(self, days: int = 7) -> List[Dict[str, Any]]
    def get_active_projects(self, days: int = 14) -> List[str]
```

### UpdateCard

Represents an update card.

```python
class UpdateCard:
    id: str
    title: str
    category: str
    summary: str
    details: Dict[str, Any]
    actions: List[str]
    sources: List[Dict[str, str]]
    priority: str  # low, medium, high
    tags: List[str]
    timestamp: str

    def to_markdown(self, detail_level: str = "detailed") -> str
    def to_dict(self) -> Dict[str, Any]
```

## CLI Reference

### Commands

```
pulse generate [-o OUTPUT] [-f FORMAT]
  Generate a pulse update

pulse status
  Show system status

pulse config [OPTIONS]
  Manage configuration
  --set KEY=VALUE       Set configuration value
  --add-interest TOPIC  Add user interest
  --remove-interest     Remove interest
  --add-metric METRIC   Add tracked metric
  --show                Show current config

pulse add [-f FILE]
  Add conversation to memory

pulse feedback CARD_ID TYPE [-n NOTES]
  Record feedback on a card
  TYPE: up, down, dismiss, save, share

pulse history [-c COUNT] [-v]
  Show pulse history

pulse scheduler ACTION
  Manage scheduler
  ACTION: start, stop, status, run
```

## Advanced Topics

### Custom Agents

Create custom agents to extend functionality:

```python
class CustomAnalyzer:
    def __init__(self, memory_store):
        self.memory_store = memory_store

    def analyze(self):
        # Your custom analysis
        return insights
```

### Custom Card Types

Generate custom update cards:

```python
from agent_pulse.generators.card_generator import UpdateCard

custom_card = UpdateCard(
    id="custom_001",
    title="Custom Insight",
    category="custom",
    summary="Your summary here",
    details={"key": "value"},
    actions=["Action 1", "Action 2"],
    priority="high",
    tags=["custom"],
)
```

### Integration Examples

#### Web Search Integration

```python
# Placeholder for future WebSearch integration
class EnhancedResearchAgent(ResearchAgent):
    def research_topic(self, topic):
        # Call WebSearch tool
        # Process results
        return research_data
```

#### Calendar Integration

```python
# Placeholder for calendar integration
def get_upcoming_events():
    # Fetch calendar events
    # Generate reminder cards
    pass
```

### Performance Optimization

For large conversation histories:

1. **Limit lookback**: Reduce `lookback_days` to 3-7 days
2. **Batch processing**: Process conversations in batches
3. **Cache results**: Research agent caches for 1 hour
4. **Selective agents**: Disable agents you don't need

### Data Privacy

Agent Pulse stores data locally in `~/.agent_pulse/`:
- Conversations are stored with unique IDs
- No data is sent to external services (currently)
- You control all stored data

To clear data:
```bash
rm -rf ~/.agent_pulse/
```

## Troubleshooting

### No Updates Generated

**Problem**: `generate` produces no cards

**Solutions**:
1. Ensure you've added conversations
2. Check `lookback_days` covers period with conversations
3. Verify conversations meet `min_conversation_length`
4. Review config with `pulse config --show`

### Scheduler Not Running

**Problem**: Scheduled updates don't run

**Solutions**:
1. Verify `schedule_enabled = True`
2. Check schedule time and frequency
3. Ensure process stays running (use systemd/supervisor)
4. Check logs for errors

### Poor Personalization

**Problem**: Updates aren't relevant

**Solutions**:
1. Provide more feedback (thumbs up/down)
2. Add your interests: `pulse config --add-interest "topic"`
3. Ensure sufficient conversation history (10+ conversations)
4. Review and adjust category weights

### Import Errors

**Problem**: `ModuleNotFoundError: agent_pulse`

**Solutions**:
1. Ensure you're in ClaudeCodeFrameWork directory
2. Add to PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:/path/to/ClaudeCodeFrameWork"`
3. Use absolute imports in scripts

### Memory Issues

**Problem**: System uses too much memory

**Solutions**:
1. Reduce `max_conversations_to_analyze`
2. Decrease `lookback_days`
3. Clear old pulse history periodically
4. Limit `max_topics_per_update`

---

## Support & Contributing

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub discussions
- **Contributing**: See CONTRIBUTING.md

## License

MIT License - see LICENSE file for details
