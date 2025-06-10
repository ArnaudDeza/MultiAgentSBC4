"""
Pre-defined debate topics for the multi-agent debate system.
"""

# Dictionary of debate topics, framed as statements.
DEBATE_TOPICS = {
    "pineapple_pizza": "Pineapple is a valid and delicious pizza topping.",
    "four_day_workweek": "The standard work week should be reduced to four days for all industries.",
    "ai_education": "Artificial intelligence should be used to replace human teachers in most classroom settings.",
    "social_media": "Social media platforms have caused more harm than good to modern society.",
    "college_free": "Higher education (college and university) should be provided free of charge to all qualified students.",
}


def get_topic(topic_key: str) -> str:
    """
    Get a debate topic by its key.
    
    Args:
        topic_key: The key for the desired topic
        
    Returns:
        The debate topic question, or None if not found
    """
    return DEBATE_TOPICS.get(topic_key)


def list_topic_keys() -> list:
    """Return a list of topic keys."""
    return list(DEBATE_TOPICS.keys())


def list_topics() -> None:
    """Print all available topics."""
    print("Available Debate Topics:")
    print("=" * 50)
    for key, value in DEBATE_TOPICS.items():
        print(f"  {key}: {value}")
    print("=" * 50)


if __name__ == "__main__":
    list_topics() 