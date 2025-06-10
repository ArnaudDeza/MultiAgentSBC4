"""
Pre-defined event scenarios for the press conference simulator.
"""

PRESS_CONFERENCE_EVENTS = {
    "tech_product_launch": {
        "title": "QuantumCore Nexus-1 Chip Launch",
        "details": "QuantumCore Inc. has just announced the launch of the 'Nexus-1', a consumer-grade quantum computing chip. They claim it is 1,000 times more powerful than existing processors. The launch event was today, but details on pricing and public availability are still scarce."
    },
    "environmental_disaster": {
        "title": "MegaCorp Oil Spill",
        "details": "An oil tanker owned by MegaCorp has run aground off the coast of the Galapagos Islands, causing a significant oil spill. Environmental groups are reporting major damage to the local ecosystem. The cause of the incident is currently under investigation, but initial reports suggest a possible navigation system failure."
    },
    "political_scandal": {
        "title": "Minister Chen Misuse of Funds Allegation",
        "details": "Leaked documents suggest that a high-ranking government official, Minister Alex Chen, may have used public funds for personal vacations. The documents, published by an anonymous source, include receipts and travel itineraries. The government has yet to issue a formal response but has confirmed the authenticity of the documents."
    },
    "scientific_breakthrough": {
        "title": "Global Health Institute's 'CogniClear' Drug",
        "details": "Researchers at the Global Health Institute have announced a major breakthrough in Alzheimer's research. Their new drug, 'CogniClear', has shown in early trials to reverse memory loss by up to 50%. The drug is now entering Phase 3 clinical trials, and the institute is seeking funding for mass production."
    }
}

def list_event_keys() -> list:
    """Return a list of event keys."""
    return list(PRESS_CONFERENCE_EVENTS.keys())

def list_events() -> None:
    """Print all available events."""
    print("Available Press Conference Scenarios:")
    print("=" * 50)
    for key, value in PRESS_CONFERENCE_EVENTS.items():
        print(f"  {key}: {value['title']}")
    print("=" * 50)

def get_event(event_key: str) -> dict:
    """Get an event by its key."""
    return PRESS_CONFERENCE_EVENTS.get(event_key) 