#!/usr/bin/env python3
"""
Demo script showing how the topic resolution works in the orchestrator.
"""

import sys
from topics import get_topic, list_topics, list_topic_keys, DEBATE_TOPICS

def resolve_topic(topic_input: str) -> str:
    """
    Resolve topic input to actual topic question.
    
    Args:
        topic_input: Either a topic key or a custom topic question
        
    Returns:
        The resolved topic question
    """
    # First, check if it's a predefined topic key
    predefined_topic = get_topic(topic_input)
    if predefined_topic:
        print(f"✅ Using predefined topic '{topic_input}': {predefined_topic}")
        return predefined_topic
    else:
        # Use as custom topic
        print(f"🆕 Using custom topic: {topic_input}")
        return topic_input

def demo():
    """Demonstrate topic resolution with examples."""
    print("🎯 Multi-Agent Debate Topic System Demo")
    print("=" * 50)
    
    # Demo 1: Predefined topics
    print("\n1️⃣  PREDEFINED TOPICS:")
    examples = ["pineapple_pizza", "ai_education", "nuclear_energy", "universal_income"]
    
    for topic_key in examples:
        topic = resolve_topic(topic_key)
        print(f"   Key: {topic_key}")
        print(f"   Topic: {topic}")
        print()
    
    # Demo 2: Custom topics  
    print("\n2️⃣  CUSTOM TOPICS:")
    custom_examples = [
        "Should cats rule the world?",
        "Is pineapple on pizza a crime against humanity?",
        "Should we replace all politicians with AI?",
        "Is cereal soup?"
    ]
    
    for custom_topic in custom_examples:
        topic = resolve_topic(custom_topic)
        print()
    
    # Demo 3: Show how to use it
    print("\n3️⃣  HOW TO USE:")
    print("   🔹 Predefined topic: python orchestrator.py --topic pineapple_pizza")
    print("   🔹 Custom topic:     python orchestrator.py --topic 'Should cats rule the world?'")
    print("   🔹 List topics:      python orchestrator.py --list-topics")
    print("   🔹 List keys only:   python orchestrator.py --list-keys")
    
    print(f"\n📊 Total predefined topics available: {len(DEBATE_TOPICS)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Demo with command line argument
        topic_input = sys.argv[1]
        print(f"Demo resolving: {topic_input}")
        resolved = resolve_topic(topic_input)
        print(f"Resolved to: {resolved}")
    else:
        # Full demo
        demo() 