"""
Pre-defined negotiation scenarios for the simulator.
Each scenario includes public information and secret goals for the agents.
"""

NEGOTIATION_SCENARIOS = {
    "yard_sale_lamp": {
        "name": "Local Yard Sale",
        "item_name": "a dusty but charming vintage lamp",
        "list_price": 40,
        "seller_personality": "friendly but a little attached to their old items",
        "seller_min_price": 20,
        "buyer_desire_level": "medium",
        "buyer_target_price": 25,
        "buyer_max_price": 35,
    },
    "fish_market": {
        "name": "Busy Fish Market",
        "item_name": "the last fresh tuna of the day",
        "list_price": 75,
        "seller_personality": "a bit gruff and in a hurry to close up shop",
        "seller_min_price": 55,
        "buyer_desire_level": "high",
        "buyer_target_price": 60,
        "buyer_max_price": 70,
    },
    "pokemon_card": {
        "name": "Comic Book Store",
        "item_name": "a rare, holographic Charizard card",
        "list_price": 500,
        "seller_personality": "a savvy and expert collector who knows the card's value",
        "seller_min_price": 420,
        "buyer_desire_level": "very high",
        "buyer_target_price": 440,
        "buyer_max_price": 480,
    }
}

def list_scenario_keys() -> list:
    """Return a list of scenario keys."""
    return list(NEGOTIATION_SCENARIOS.keys())

def list_scenarios() -> None:
    """Print all available scenarios."""
    print("Available Negotiation Scenarios:")
    print("=" * 50)
    for key, value in NEGOTIATION_SCENARIOS.items():
        print(f"  {key}: A negotiation for '{value['item_name']}' at a {value['name']}.")
    print("=" * 50)

def get_scenario(scenario_key: str) -> dict:
    """Get a scenario by its key."""
    return NEGOTIATION_SCENARIOS.get(scenario_key) 