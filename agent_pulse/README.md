# Agent Pulse

A ChatGPT Pulse-inspired proactive AI assistant system that analyzes conversations, conducts research, and delivers personalized updates to help you stay on top of tasks, opportunities, and interests.

## Overview

**Agent Pulse** transforms your AI assistant from reactive to proactive by:

- 📊 **Analyzing past conversations** to understand your interests, projects, and challenges
- 🔍 **Conducting overnight research** on topics relevant to you
- 💡 **Identifying opportunities** based on your work and interests
- 🔧 **Suggesting solutions** to recurring problems
- ✅ **Tracking action items** and commitments
- 📰 **Delivering updates** as visual cards you can scan and act on

## Features

### Core Capabilities

1. **Conversation Analysis**
   - Extracts topics, entities, and themes from past conversations
   - Identifies action items, problems, and opportunities
   - Tracks trending topics and active projects

2. **Proactive Research**
   - Conducts research on topics of interest
   - Finds recent developments and news
   - Suggests learning resources and tutorials

3. **Opportunity Finding**
   - Identifies learning opportunities based on your interests
   - Suggests optimizations for recurring problems
   - Finds connections between different topics
   - Highlights trend-based opportunities

4. **Problem Solving**
   - Analyzes recurring issues
   - Suggests known solutions and debugging strategies
   - Recommends preventive measures
   - Identifies quick wins

5. **Personalization**
   - Learns from your feedback (thumbs up/down, save, dismiss)
   - Adapts to your preferences over time
   - Focuses on topics and categories you care about

6. **Scheduled Updates**
   - Runs automatically on a schedule (daily/weekly)
   - Delivers updates at your preferred time
   - Can be triggered manually anytime

## Installation

```bash
# Navigate to the ClaudeCodeFrameWork directory
cd ClaudeCodeFrameWork

# The agent_pulse package is already included
# No additional installation needed!
```

## Quick Start

### 1. Using Python API

```python
from agent_pulse import PulseOrchestrator, PulseConfig

# Initialize with default configuration
orchestrator = PulseOrchestrator()

# Add some conversations to analyze
conversations = [
    {
        "messages": [
            {"role": "user", "content": "I'm working on a machine learning project"},
            {"role": "assistant", "content": "Great! What kind of ML project?"},
            {"role": "user", "content": "Building a recommendation system"},
        ]
    }
]

for conv in conversations:
    orchestrator.add_conversation(conv["messages"])

# Generate a pulse update
pulse_update = orchestrator.generate_pulse_update()

# Render as markdown
markdown_output = orchestrator.render_pulse_update(pulse_update)
print(markdown_output)

# Save to file
with open("pulse_update.md", "w") as f:
    f.write(markdown_output)
```

### 2. Using CLI

```bash
# Generate a pulse update
python -m agent_pulse.cli.pulse_cli generate

# Save to file
python -m agent_pulse.cli.pulse_cli generate -o pulse.md

# Check system status
python -m agent_pulse.cli.pulse_cli status

# Add a conversation
python -m agent_pulse.cli.pulse_cli add -f conversation.json

# Configure interests
python -m agent_pulse.cli.pulse_cli config --add-interest "machine learning"
python -m agent_pulse.cli.pulse_cli config --add-interest "web development"

# Start scheduler
python -m agent_pulse.cli.pulse_cli scheduler start
```

## Configuration

### Basic Configuration

```python
from agent_pulse import PulseConfig
from datetime import time

config = PulseConfig()

# Scheduling
config.schedule_enabled = True
config.schedule_time = time(6, 0)  # 6:00 AM
config.schedule_frequency = "daily"  # or "weekly", "manual"

# Analysis settings
config.lookback_days = 7
config.max_conversations_to_analyze = 50

# User preferences
config.user_interests = ["machine learning", "python", "web development"]
config.tracked_metrics = ["project progress", "code quality"]
config.focus_areas = ["performance", "scalability"]

# Card settings
config.card_style = "detailed"  # or "minimal", "comprehensive"
config.max_topics_per_update = 8

# Save configuration
config.save()
```

### CLI Configuration

```bash
# Set schedule time
python -m agent_pulse.cli.pulse_cli config --set schedule_time=06:00

# Set frequency
python -m agent_pulse.cli.pulse_cli config --set schedule_frequency=daily

# Add interests
python -m agent_pulse.cli.pulse_cli config --add-interest "data science"

# Show current config
python -m agent_pulse.cli.pulse_cli config --show
```

## Update Cards

Agent Pulse generates different types of update cards:

### 1. Research Cards 🔍
Updates on topics you're interested in, with key findings and resources.

### 2. Problem Solution Cards 🔧
Suggested solutions for problems mentioned in conversations.

### 3. Opportunity Cards 💡
Learning opportunities, optimizations, and trend-based suggestions.

### 4. Action Items Cards ✅
Summary of pending tasks and commitments.

### 5. Metrics Cards 📊
Updates on tracked metrics and progress.

### 6. News Cards 📰
Recent news and developments in your areas of interest.

## Feedback System

Agent Pulse learns from your feedback to personalize future updates:

```python
# Record feedback on a card
orchestrator.record_feedback(
    card_id="abc123...",
    feedback_type="thumbs_up",  # or "thumbs_down", "dismiss", "save", "share"
    notes="Very helpful!"
)
```

```bash
# CLI feedback
python -m agent_pulse.cli.pulse_cli feedback <card_id> up
python -m agent_pulse.cli.pulse_cli feedback <card_id> down -n "Not relevant"
```

The system adjusts:
- Topic weights (boost topics you like, reduce ones you don't)
- Category weights (prioritize card types you engage with)
- Favorite topics (highlighted in future updates)
- Dismissed topics (filtered out)

## Scheduler

Run pulse updates automatically:

```python
# Start scheduler in background
orchestrator.start_scheduler()

# Stop scheduler
orchestrator.stop_scheduler()

# Run immediately
orchestrator.scheduler.run_now()

# Get scheduler status
status = orchestrator.scheduler.get_status()
```

```bash
# CLI scheduler management
python -m agent_pulse.cli.pulse_cli scheduler start
python -m agent_pulse.cli.pulse_cli scheduler status
python -m agent_pulse.cli.pulse_cli scheduler run
python -m agent_pulse.cli.pulse_cli scheduler stop
```

## Architecture

```
agent_pulse/
├── core/
│   ├── orchestrator.py      # Main coordinator
│   ├── scheduler.py          # Scheduling logic
│   └── config.py            # Configuration management
├── agents/
│   ├── conversation_analyzer.py  # Analyzes conversations
│   ├── research_agent.py         # Conducts research
│   ├── opportunity_finder.py     # Finds opportunities
│   └── problem_solver.py         # Suggests solutions
├── storage/
│   ├── memory_store.py      # Conversation storage
│   └── preferences.py       # User preferences & feedback
├── generators/
│   └── card_generator.py    # Creates update cards
├── integrations/
│   └── (future integrations)
└── cli/
    └── pulse_cli.py         # Command-line interface
```

## Data Storage

Agent Pulse stores data in `~/.agent_pulse/`:

```
~/.agent_pulse/
├── config.json              # Configuration
├── preferences.json         # User preferences
├── feedback_history.json    # Feedback data
├── memory/                  # Conversation storage
│   ├── index.json
│   └── <conversation_id>.json
├── conversations/           # Raw conversation history
└── pulse_history/           # Past pulse updates
    └── pulse_<timestamp>.json
```

## Examples

See the `examples/` directory for:

- `basic_usage.py` - Simple usage examples
- `advanced_usage.py` - Advanced features and customization
- `custom_agents.py` - Creating custom agents
- `integration_examples.py` - Integration with external services

## API Reference

### PulseOrchestrator

Main class for coordinating pulse updates.

**Methods:**
- `add_conversation(messages, metadata)` - Add a conversation
- `generate_pulse_update()` - Generate new pulse update
- `render_pulse_update(pulse_update, format)` - Render update
- `record_feedback(card_id, feedback_type, notes)` - Record feedback
- `start_scheduler()` - Start automatic scheduling
- `stop_scheduler()` - Stop scheduler
- `get_status()` - Get system status

### ConversationAnalyzer

Analyzes conversations to extract insights.

**Methods:**
- `analyze_conversation(conversation)` - Analyze single conversation
- `analyze_recent_conversations(days, max_count)` - Analyze recent conversations
- `get_trending_topics(days)` - Get trending topics
- `get_active_projects(days)` - Identify active projects

### ResearchAgent

Conducts research on topics.

**Methods:**
- `research_topic(topic, focus_areas, include_news, include_tutorials)` - Research a topic
- `research_multiple_topics(topics, max_topics)` - Research multiple topics
- `get_trending_in_field(field, days)` - Get trending topics in a field
- `check_for_updates(tracked_topics, since_hours)` - Check for topic updates

### OpportunityFinder

Identifies opportunities.

**Methods:**
- `find_opportunities(topics, entities, user_interests, days)` - Find opportunities
- `suggest_next_actions(opportunities, max_suggestions)` - Suggest actions
- `identify_knowledge_gaps(topics, user_interests)` - Find knowledge gaps

### ProblemSolver

Analyzes problems and suggests solutions.

**Methods:**
- `analyze_problems(days, max_problems)` - Analyze recent problems
- `suggest_preventive_measures(recurring_problems)` - Suggest preventive measures
- `get_solution_quick_wins(problems)` - Identify quick-win solutions

## Customization

### Custom Agents

You can create custom agents by extending the base functionality:

```python
class CustomAgent:
    def __init__(self, memory_store):
        self.memory_store = memory_store

    def analyze(self, days=7):
        # Your custom analysis logic
        pass
```

### Custom Card Types

Create custom update cards:

```python
from agent_pulse.generators.card_generator import UpdateCard

custom_card = UpdateCard(
    id="custom_001",
    title="Custom Update",
    category="custom",
    summary="Your custom summary",
    details={"key": "value"},
    actions=["Action 1", "Action 2"],
    priority="high",
    tags=["custom", "important"],
)
```

## Integration with Claude Code

Agent Pulse is designed to work seamlessly with Claude Code workflows:

1. **Conversation History**: Automatically tracks Claude Code conversations
2. **Project Context**: Understands your codebase and projects
3. **Development Workflow**: Integrates with your development cycle
4. **Proactive Assistance**: Surfaces relevant information when you need it

## Best Practices

1. **Regular Conversations**: Have meaningful conversations with Claude to build context
2. **Provide Feedback**: Use thumbs up/down to improve personalization
3. **Set Interests**: Configure your interests and focus areas
4. **Review Updates**: Check pulse updates regularly
5. **Act on Suggestions**: Follow through on action items and opportunities

## Troubleshooting

### No updates generated
- Ensure you have added conversations to memory
- Check that `lookback_days` covers a period with conversations
- Verify configuration with `config --show`

### Scheduler not running
- Check `schedule_enabled = True` in configuration
- Verify schedule time and frequency settings
- Ensure the process stays running (use systemd or similar)

### Poor personalization
- Provide more feedback on cards
- Add your interests and focus areas
- Ensure sufficient conversation history

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Core agent implementation
- ✅ Conversation analysis
- ✅ Update card generation
- ✅ CLI interface
- ✅ Feedback learning

### Phase 2: Integrations (Planned)
- [ ] Web search integration (live)
- [ ] Calendar integration
- [ ] Email integration
- [ ] GitHub integration
- [ ] Slack/Discord notifications

### Phase 3: Advanced Features (Future)
- [ ] Multi-user support
- [ ] Team collaboration features
- [ ] Advanced analytics and insights
- [ ] Custom plugin system
- [ ] Web dashboard

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Contact

For questions, issues, or suggestions, please open a GitHub issue.

---

**Agent Pulse** - Your proactive AI assistant that works while you sleep! 🌅
