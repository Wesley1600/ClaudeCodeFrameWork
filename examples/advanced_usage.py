#!/usr/bin/env python3
"""
Advanced Usage Example for Agent Pulse

This example demonstrates:
- Custom configuration
- Preference management
- Scheduler usage
- Advanced filtering
- Feedback analysis
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_pulse import PulseOrchestrator, PulseConfig
from agent_pulse.storage.preferences import FeedbackType
from datetime import datetime, time
import time as time_module


def main():
    print("="*60)
    print("Agent Pulse - Advanced Usage Example")
    print("="*60)

    # Create custom configuration
    print("\n1. Creating custom configuration...")
    config = PulseConfig()

    # Scheduling configuration
    config.schedule_enabled = True
    config.schedule_time = time(6, 0)  # 6:00 AM
    config.schedule_frequency = "daily"

    # Analysis settings
    config.lookback_days = 14  # Look back 2 weeks
    config.max_conversations_to_analyze = 100

    # Enable/disable specific agents
    config.enable_conversation_analysis = True
    config.enable_research = True
    config.enable_opportunity_finding = True
    config.enable_problem_solving = True

    # Research settings
    config.max_web_searches = 5
    config.max_topics_per_update = 10

    # Card customization
    config.card_style = "comprehensive"
    config.include_sources = True
    config.include_action_items = True

    # User preferences
    config.user_interests = [
        "machine learning",
        "natural language processing",
        "computer vision",
        "reinforcement learning",
        "MLOps",
    ]

    config.tracked_metrics = [
        "model accuracy",
        "training time",
        "inference speed",
    ]

    config.focus_areas = [
        "performance optimization",
        "model interpretability",
        "production deployment",
    ]

    # Save configuration
    config.save()
    print("   Configuration saved")

    # Initialize orchestrator
    print("\n2. Initializing orchestrator with custom config...")
    orchestrator = PulseOrchestrator(config)

    # Add diverse conversations
    print("\n3. Adding diverse conversations...")
    conversations = [
        # ML Development
        {
            "messages": [
                {"role": "user", "content": "Working on a transformer model for sentiment analysis."},
                {"role": "assistant", "content": "Great! Are you using pre-trained models?"},
                {"role": "user", "content": "Yes, fine-tuning BERT. Having memory issues with large batches."},
            ]
        },
        # Problem Solving
        {
            "messages": [
                {"role": "user", "content": "Getting CUDA out of memory errors consistently."},
                {"role": "assistant", "content": "Try reducing batch size or using gradient accumulation."},
                {"role": "user", "content": "I'll implement gradient checkpointing too."},
            ]
        },
        # Opportunity
        {
            "messages": [
                {"role": "user", "content": "Thinking about implementing model quantization for faster inference."},
                {"role": "assistant", "content": "Quantization can significantly reduce model size."},
                {"role": "user", "content": "I should research INT8 quantization techniques."},
            ]
        },
        # Learning
        {
            "messages": [
                {"role": "user", "content": "Want to learn about diffusion models and how they work."},
                {"role": "assistant", "content": "Diffusion models are fascinating! They work by..."},
                {"role": "user", "content": "This could be useful for data augmentation in my project."},
            ]
        },
        # Action Items
        {
            "messages": [
                {"role": "user", "content": "Need to set up MLflow for experiment tracking."},
                {"role": "assistant", "content": "MLflow is great for managing ML experiments."},
                {"role": "user", "content": "I should also integrate it with my training pipeline."},
            ]
        },
    ]

    for conv in conversations:
        orchestrator.add_conversation(conv["messages"])
    print(f"   Added {len(conversations)} conversations")

    # Generate pulse update
    print("\n4. Generating comprehensive pulse update...")
    pulse_update = orchestrator.generate_pulse_update()

    # Analyze the update
    print("\n5. Analyzing pulse update...")
    print(f"   Total cards: {pulse_update['summary']['total_cards']}")
    print("   Cards by category:")
    for category, count in pulse_update['summary']['by_category'].items():
        print(f"     - {category}: {count}")

    # Simulate user feedback
    print("\n6. Simulating user feedback...")
    for i, card_dict in enumerate(pulse_update["cards"][:3]):
        feedback_types = ["thumbs_up", "save", "thumbs_down"]
        feedback = feedback_types[i % 3]

        orchestrator.record_feedback(
            card_id=card_dict["id"],
            feedback_type=feedback,
            notes=f"Feedback for card {i+1}"
        )
        print(f"   Card {i+1}: {feedback}")

    # Get feedback summary
    print("\n7. Feedback summary...")
    feedback_summary = orchestrator.preference_manager.get_feedback_summary(days=30)
    print(f"   Total feedback recorded: {feedback_summary['total_feedback']}")
    print(f"   By type: {feedback_summary['by_type']}")

    # Manage preferences
    print("\n8. Managing preferences...")

    # Add favorite topics
    orchestrator.preference_manager.add_favorite_topic("machine learning")
    orchestrator.preference_manager.add_favorite_topic("deep learning")
    print(f"   Favorite topics: {orchestrator.preference_manager.get_favorite_topics()}")

    # Adjust card preferences
    orchestrator.preference_manager.set_preferred_card_count(8)
    orchestrator.preference_manager.set_detail_level("comprehensive")
    print("   Updated card preferences")

    # Get all preferences
    prefs = orchestrator.preference_manager.get_preferences_dict()
    print(f"   Category weights: {prefs['category_weights']}")

    # Demonstrate scheduler (without actually running it)
    print("\n9. Scheduler configuration...")
    scheduler_status = orchestrator.scheduler.get_status()
    print(f"   Enabled: {scheduler_status['enabled']}")
    print(f"   Frequency: {scheduler_status['frequency']}")
    print(f"   Schedule time: {scheduler_status['schedule_time']}")
    if scheduler_status['next_run']:
        print(f"   Next run: {scheduler_status['next_run']}")

    # View pulse history
    print("\n10. Pulse history...")
    history = orchestrator.get_pulse_history(count=5)
    print(f"   Total pulse updates: {len(history)}")
    for i, entry in enumerate(history, 1):
        print(f"   {i}. {entry['timestamp']} - {entry['card_count']} cards")

    # Get system status
    print("\n11. System status...")
    status = orchestrator.get_status()
    print(f"   Memory store stats:")
    print(f"     - Total conversations: {status['memory_store']['total_conversations']}")
    print(f"     - Recent (7d): {status['memory_store']['recent_conversations_7d']}")
    print(f"     - Unique topics: {status['memory_store']['unique_topics']}")

    # Save final configuration
    print("\n12. Saving final configuration...")
    config.save()
    print("   Configuration saved to ~/.agent_pulse/config.json")

    print("\n" + "="*60)
    print("Advanced usage example completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
