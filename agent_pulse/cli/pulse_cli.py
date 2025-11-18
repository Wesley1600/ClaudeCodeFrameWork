#!/usr/bin/env python3
"""
Agent Pulse CLI

Command-line interface for managing the Agent Pulse system.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, time
import json

from ..core.orchestrator import PulseOrchestrator
from ..core.config import PulseConfig
from ..storage.memory_store import ConversationEntry
from ..storage.preferences import FeedbackType


def cmd_generate(args):
    """Generate a pulse update."""
    config = PulseConfig.load()
    orchestrator = PulseOrchestrator(config)

    print("Generating pulse update...")
    pulse_update = orchestrator.generate_pulse_update()

    if args.output:
        output_path = Path(args.output)
        output_format = args.format or "markdown"

        content = orchestrator.render_pulse_update(pulse_update, output_format)

        with open(output_path, 'w') as f:
            f.write(content)

        print(f"\nPulse update saved to: {output_path}")
    else:
        # Print to console
        print("\n" + "="*60)
        print(orchestrator.render_pulse_update(pulse_update, "markdown"))
        print("="*60)


def cmd_status(args):
    """Show system status."""
    config = PulseConfig.load()
    orchestrator = PulseOrchestrator(config)

    status = orchestrator.get_status()

    print("\n📊 Agent Pulse Status")
    print("="*60)

    # Memory store stats
    print("\n💾 Memory Store:")
    mem_stats = status["memory_store"]
    print(f"  Total conversations: {mem_stats['total_conversations']}")
    print(f"  Recent (7 days): {mem_stats['recent_conversations_7d']}")
    print(f"  Unique topics: {mem_stats['unique_topics']}")

    # Scheduler status
    print("\n⏰ Scheduler:")
    sched = status["scheduler"]
    print(f"  Enabled: {sched['enabled']}")
    print(f"  Running: {sched['running']}")
    print(f"  Frequency: {sched['frequency']}")
    print(f"  Schedule time: {sched['schedule_time']}")
    if sched['last_run']:
        print(f"  Last run: {sched['last_run']}")
    if sched['next_run']:
        print(f"  Next run: {sched['next_run']}")

    # Configuration
    print("\n⚙️  Configuration:")
    conf = status["config"]
    print(f"  Lookback days: {conf['lookback_days']}")
    print(f"  Max topics per update: {conf['max_topics']}")

    # Preferences
    print("\n🎯 Preferences:")
    prefs = status["preferences"]
    print(f"  User interests: {', '.join(prefs['user_interests']) if prefs['user_interests'] else 'None set'}")
    print(f"  Favorite topics: {', '.join(prefs['favorite_topics']) if prefs['favorite_topics'] else 'None'}")

    print("\n" + "="*60 + "\n")


def cmd_config(args):
    """Manage configuration."""
    config = PulseConfig.load()

    if args.set:
        key, value = args.set.split('=', 1)

        if key == "schedule_time":
            hour, minute = map(int, value.split(':'))
            config.schedule_time = time(hour, minute)
        elif key == "schedule_frequency":
            config.schedule_frequency = value
        elif key == "schedule_enabled":
            config.schedule_enabled = value.lower() in ['true', '1', 'yes']
        elif key == "lookback_days":
            config.lookback_days = int(value)
        elif key == "max_topics_per_update":
            config.max_topics_per_update = int(value)
        elif key == "card_style":
            config.card_style = value
        else:
            print(f"Unknown configuration key: {key}")
            return

        config.save()
        print(f"Configuration updated: {key} = {value}")

    elif args.add_interest:
        config.add_interest(args.add_interest)
        config.save()
        print(f"Added interest: {args.add_interest}")

    elif args.remove_interest:
        config.remove_interest(args.remove_interest)
        config.save()
        print(f"Removed interest: {args.remove_interest}")

    elif args.add_metric:
        config.add_tracked_metric(args.add_metric)
        config.save()
        print(f"Added metric: {args.add_metric}")

    elif args.show:
        print("\n⚙️  Current Configuration")
        print("="*60)
        print(f"Schedule enabled: {config.schedule_enabled}")
        print(f"Schedule time: {config.schedule_time}")
        print(f"Schedule frequency: {config.schedule_frequency}")
        print(f"Lookback days: {config.lookback_days}")
        print(f"Max topics per update: {config.max_topics_per_update}")
        print(f"Card style: {config.card_style}")
        print(f"User interests: {', '.join(config.user_interests) if config.user_interests else 'None'}")
        print(f"Tracked metrics: {', '.join(config.tracked_metrics) if config.tracked_metrics else 'None'}")
        print("="*60 + "\n")


def cmd_add_conversation(args):
    """Add a conversation to memory."""
    config = PulseConfig.load()
    orchestrator = PulseOrchestrator(config)

    # Read conversation from file or stdin
    if args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
            messages = data.get("messages", [])
    else:
        print("Reading conversation from stdin (JSON format)...")
        print("Expected format: {\"messages\": [{\"role\": \"user\", \"content\": \"...\"}, ...]}")
        data = json.load(sys.stdin)
        messages = data.get("messages", [])

    if not messages:
        print("Error: No messages found")
        return

    conversation = orchestrator.add_conversation(messages)
    print(f"\nConversation added successfully!")
    print(f"ID: {conversation.id}")
    print(f"Messages: {len(messages)}")
    print(f"Timestamp: {conversation.timestamp}")


def cmd_feedback(args):
    """Record feedback on a card."""
    config = PulseConfig.load()
    orchestrator = PulseOrchestrator(config)

    feedback_types = {
        "up": "thumbs_up",
        "down": "thumbs_down",
        "dismiss": "dismiss",
        "save": "save",
        "share": "share",
    }

    feedback_type = feedback_types.get(args.type, args.type)

    orchestrator.record_feedback(
        card_id=args.card_id,
        feedback_type=feedback_type,
        notes=args.notes,
    )


def cmd_history(args):
    """Show pulse history."""
    config = PulseConfig.load()
    orchestrator = PulseOrchestrator(config)

    history = orchestrator.get_pulse_history(count=args.count)

    if not history:
        print("No pulse history found")
        return

    print("\n📜 Pulse History")
    print("="*60)

    for i, entry in enumerate(history, 1):
        timestamp = datetime.fromisoformat(entry["timestamp"])
        print(f"{i}. {timestamp.strftime('%Y-%m-%d %H:%M')} - {entry['card_count']} cards")
        if args.verbose:
            print(f"   File: {entry['file']}")

    print("="*60 + "\n")


def cmd_scheduler(args):
    """Manage scheduler."""
    config = PulseConfig.load()
    orchestrator = PulseOrchestrator(config)

    if args.action == "start":
        orchestrator.start_scheduler()
        print("Scheduler started. Press Ctrl+C to stop.")
        try:
            # Keep the script running
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            orchestrator.stop_scheduler()
            print("\nScheduler stopped.")

    elif args.action == "stop":
        orchestrator.stop_scheduler()

    elif args.action == "status":
        status = orchestrator.scheduler.get_status()
        print("\n⏰ Scheduler Status")
        print("="*60)
        print(f"Enabled: {status['enabled']}")
        print(f"Running: {status['running']}")
        print(f"Frequency: {status['frequency']}")
        print(f"Schedule time: {status['schedule_time']}")
        if status['last_run']:
            print(f"Last run: {status['last_run']}")
        if status['next_run']:
            print(f"Next run: {status['next_run']}")
        print("="*60 + "\n")

    elif args.action == "run":
        orchestrator.scheduler.run_now()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Pulse - Proactive AI Assistant System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a pulse update")
    gen_parser.add_argument("-o", "--output", help="Output file path")
    gen_parser.add_argument("-f", "--format", choices=["markdown", "json"], help="Output format")
    gen_parser.set_defaults(func=cmd_generate)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.set_defaults(func=cmd_status)

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--set", help="Set configuration (key=value)")
    config_parser.add_argument("--add-interest", help="Add user interest")
    config_parser.add_argument("--remove-interest", help="Remove user interest")
    config_parser.add_argument("--add-metric", help="Add tracked metric")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    config_parser.set_defaults(func=cmd_config)

    # Add conversation command
    add_parser = subparsers.add_parser("add", help="Add a conversation to memory")
    add_parser.add_argument("-f", "--file", help="JSON file containing conversation")
    add_parser.set_defaults(func=cmd_add_conversation)

    # Feedback command
    feedback_parser = subparsers.add_parser("feedback", help="Record feedback on a card")
    feedback_parser.add_argument("card_id", help="Card ID")
    feedback_parser.add_argument("type", choices=["up", "down", "dismiss", "save", "share"], help="Feedback type")
    feedback_parser.add_argument("-n", "--notes", help="Optional notes")
    feedback_parser.set_defaults(func=cmd_feedback)

    # History command
    history_parser = subparsers.add_parser("history", help="Show pulse history")
    history_parser.add_argument("-c", "--count", type=int, default=10, help="Number of entries to show")
    history_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed information")
    history_parser.set_defaults(func=cmd_history)

    # Scheduler command
    sched_parser = subparsers.add_parser("scheduler", help="Manage scheduler")
    sched_parser.add_argument("action", choices=["start", "stop", "status", "run"], help="Scheduler action")
    sched_parser.set_defaults(func=cmd_scheduler)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
