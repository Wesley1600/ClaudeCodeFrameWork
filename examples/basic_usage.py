#!/usr/bin/env python3
"""
Basic Usage Example for Agent Pulse

This example demonstrates:
- Creating a pulse orchestrator
- Adding conversations
- Generating pulse updates
- Recording feedback
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_pulse import PulseOrchestrator, PulseConfig
from datetime import datetime


def main():
    print("="*60)
    print("Agent Pulse - Basic Usage Example")
    print("="*60)

    # Step 1: Create configuration
    print("\n1. Creating configuration...")
    config = PulseConfig()
    config.user_interests = ["machine learning", "python", "data science"]
    config.lookback_days = 7
    config.max_topics_per_update = 5
    config.card_style = "detailed"

    # Step 2: Initialize orchestrator
    print("2. Initializing pulse orchestrator...")
    orchestrator = PulseOrchestrator(config)

    # Step 3: Add sample conversations
    print("3. Adding sample conversations...")

    sample_conversations = [
        {
            "messages": [
                {"role": "user", "content": "I'm working on a machine learning project for image classification."},
                {"role": "assistant", "content": "Great! What framework are you using?"},
                {"role": "user", "content": "I'm using PyTorch. I'm having some issues with the training loop."},
                {"role": "assistant", "content": "Can you share the error message?"},
                {"role": "user", "content": "I'm getting CUDA out of memory errors. Need to optimize batch size."},
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "I need to learn more about transformers and attention mechanisms."},
                {"role": "assistant", "content": "Transformers are a powerful architecture. Would you like me to explain the basics?"},
                {"role": "user", "content": "Yes, please! Especially how self-attention works."},
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "My model is training very slowly. Any optimization tips?"},
                {"role": "assistant", "content": "There are several optimization strategies..."},
                {"role": "user", "content": "I should probably implement mixed precision training."},
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "I'm thinking about exploring reinforcement learning next."},
                {"role": "assistant", "content": "RL is fascinating! What application are you interested in?"},
                {"role": "user", "content": "Game playing agents, maybe starting with simple environments."},
            ]
        },
    ]

    for i, conv in enumerate(sample_conversations, 1):
        conversation = orchestrator.add_conversation(conv["messages"])
        print(f"   Added conversation {i}: {conversation.id[:8]}...")

    # Step 4: Generate pulse update
    print("\n4. Generating pulse update...")
    pulse_update = orchestrator.generate_pulse_update()

    # Step 5: Display the update
    print("\n5. Rendering pulse update...")
    print("\n" + "="*60)
    markdown_output = orchestrator.render_pulse_update(pulse_update)
    print(markdown_output)
    print("="*60)

    # Step 6: Save to file
    print("\n6. Saving pulse update to file...")
    output_file = f"pulse_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output_file, 'w') as f:
        f.write(markdown_output)
    print(f"   Saved to: {output_file}")

    # Step 7: Record feedback
    print("\n7. Recording feedback on cards...")
    if pulse_update["cards"]:
        first_card_id = pulse_update["cards"][0]["id"]
        orchestrator.record_feedback(
            card_id=first_card_id,
            feedback_type="thumbs_up",
            notes="Very helpful!"
        )
        print(f"   Recorded positive feedback for card: {first_card_id[:8]}...")

    # Step 8: Check status
    print("\n8. Checking system status...")
    status = orchestrator.get_status()
    print(f"   Total conversations: {status['memory_store']['total_conversations']}")
    print(f"   Recent conversations: {status['memory_store']['recent_conversations_7d']}")
    print(f"   Unique topics: {status['memory_store']['unique_topics']}")

    print("\n" + "="*60)
    print("Basic usage example completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
