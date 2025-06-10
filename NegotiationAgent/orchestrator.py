"""
Main orchestrator for the multi-agent negotiation system.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any

from agents import BuyerAgent, SellerAgent, ModeratorAgent
from config import DEFAULT_MODEL, DEFAULT_TEMP, DEFAULT_SEED
from scenarios import list_scenarios, get_scenario, list_scenario_keys

class JsonLogger:
    """Simple JSONL logger."""
    def __init__(self, path: str):
        self.path = path
        self.log_records = []
    def log(self, record: Dict[str, Any]):
        self.log_records.append(record)
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), **record}) + '\n')

def get_user_config() -> Dict[str, Any]:
    """Interactively get negotiation settings from the user."""
    print("Welcome to the Multi-Agent Negotiation Simulator!")
    print("=" * 60)
    
    list_scenarios()
    while True:
        scenario_key = input("Choose a scenario key from the list: ")
        if scenario_key in list_scenario_keys():
            break
        print("Invalid key.")
    
    while True:
        try:
            rounds = int(input("Enter max number of negotiation rounds (e.g., 3-5): "))
            if rounds > 0:
                break
        except ValueError:
            print("Please enter a valid number.")

    print("\n--- Model Selection ---")
    buyer_model = input(f"Enter model for Buyer (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL
    seller_model = input(f"Enter model for Seller (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL
    moderator_model = input(f"Enter model for Moderator (default: {DEFAULT_MODEL}): ") or DEFAULT_MODEL

    return {
        "scenario_key": scenario_key,
        "rounds": rounds,
        "buyer_model": buyer_model,
        "seller_model": seller_model,
        "moderator_model": moderator_model,
        "temp": DEFAULT_TEMP,
        "seed": DEFAULT_SEED,
    }

def create_results_folder(scenario_key: str) -> str:
    """Create a timestamped results folder."""
    base_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(base_dir, exist_ok=True)
    folder_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{scenario_key}"
    results_folder = os.path.join(base_dir, folder_name)
    os.makedirs(results_folder, exist_ok=True)
    return results_folder

def format_chat_history(log_records: list) -> str:
    """Formats the log into a readable string for the prompts."""
    return "\n".join([f"{r['role']}: {r['message']}" for r in log_records if r.get('type') == 'negotiation_turn'])

def run_negotiation(config: Dict[str, Any]):
    """Main function to run the simulation."""
    start_time = time.time()
    scenario = get_scenario(config["scenario_key"])
    results_folder = create_results_folder(config["scenario_key"])
    
    # Setup paths and logger
    transcript_path = os.path.join(results_folder, "transcript.jsonl")
    metadata_path = os.path.join(results_folder, "metadata.json")
    summary_path = os.path.join(results_folder, "summary.md")
    logger = JsonLogger(transcript_path)
    logger.log({"event": "negotiation_start", "config": config, "scenario": scenario})

    # Initialize Agents
    buyer = BuyerAgent(config["buyer_model"], config["temp"], config["seed"], scenario)
    seller = SellerAgent(config["seller_model"], config["temp"], config["seed"] + 1, scenario)
    moderator = ModeratorAgent(config["moderator_model"], config["temp"], config["seed"] + 2)

    print("\n" + "="*60)
    print(f"Starting Negotiation: '{scenario['item_name']}' at a {scenario['name']}")
    print(f"Listed Price: ${scenario['list_price']}")
    print("="*60 + "\n")

    chat_history = ""
    last_buyer_offer = 0
    last_seller_offer = scenario['list_price']
    final_price = 0
    deal_made = False

    for r in range(config["rounds"] * 2): # Each round has a seller and buyer turn
        turn_type = "Seller" if r % 2 == 0 else "Buyer"
        
        if deal_made: break

        print(f"\n--- Turn {r//2 + 1}: {turn_type}'s Move ---")
        chat_history = format_chat_history(logger.log_records)
        
        if turn_type == "Seller":
            price, message = seller.act(chat_history)
            last_seller_offer = price if price is not None else last_seller_offer
            print(f"Seller says: {message}")
            print(f"Seller's Price: ${last_seller_offer}")
            logger.log({"role": "Seller", "message": message, "price": last_seller_offer, "type": "negotiation_turn"})
        else: # Buyer's turn
            price, message = buyer.act(chat_history)
            last_buyer_offer = price if price is not None else last_buyer_offer
            print(f"Buyer says: {message}")
            print(f"Buyer's Offer: ${last_buyer_offer}")
            logger.log({"role": "Buyer", "message": message, "price": last_buyer_offer, "type": "negotiation_turn"})

        # Check for a deal
        if last_buyer_offer >= last_seller_offer:
            deal_made = True
            final_price = last_seller_offer # Deal is made at the seller's asking price
            print(f"\nDEAL! A deal was struck at ${final_price}")
            logger.log({"event": "deal_made", "price": final_price})
            break

    if not deal_made:
        print("\nNO DEAL! The negotiation ended without an agreement.")
        logger.log({"event": "no_deal"})

    # Moderator analysis
    print("\n" + "="*60)
    print("--- Moderator's Analysis ---")
    transcript_str = format_chat_history(logger.log_records)
    analysis = moderator.analyze(transcript_str, final_price, scenario)
    print(analysis)
    logger.log({"role": "Moderator", "message": analysis, "type": "analysis"})
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# Negotiation Analysis\n\n**Outcome:** {'Deal at $' + str(final_price) if deal_made else 'No Deal'}\n\n{analysis}")

    # Save final metadata
    duration = time.time() - start_time
    final_metadata = {"config": config, "scenario": scenario, "outcome": {"deal_made": deal_made, "final_price": final_price}, "timing": {"duration_seconds": round(duration, 2)}}
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(final_metadata, f, indent=4)
        
    print("\n" + "="*60)
    print(f"Negotiation finished. Results saved in: {results_folder}")

if __name__ == "__main__":
    user_config = get_user_config()
    run_negotiation(user_config) 