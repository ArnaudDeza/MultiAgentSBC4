"""Main orchestrator for the buyer-seller negotiation simulation."""

import argparse
import random
import sys
from typing import Tuple

import config
from utils import JsonLogger
from agents import BuyerAgent, SellerAgent, MediatorAgent


def run_negotiation(min_price: float, max_price: float, max_rounds: int, threshold: float,
                   model: str, temp: float, seed: int, output: str) -> None:
    """Run the complete negotiation simulation.
    
    Args:
        min_price: Minimum acceptable price in the negotiation range
        max_price: Maximum acceptable price in the negotiation range
        max_rounds: Maximum number of negotiation rounds
        threshold: Convergence threshold for agreement (as a fraction)
        model: Ollama model name to use
        temp: Temperature setting for text generation
        seed: Random seed for reproducibility
        output: Output file path for the transcript
    """
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Initialize logger
    logger = JsonLogger(output)
    
    # Initialize agents with different seeds to ensure varied behavior
    buyer = BuyerAgent(model, temp, seed, min_price, max_price)
    seller = SellerAgent(model, temp, seed + 1, min_price, max_price)
    mediator = MediatorAgent(model, temp, seed + 2)
    
    print(f"💰 Starting Buyer-Seller Negotiation")
    print(f"📊 Model: {model}, Temperature: {temp}, Seed: {seed}")
    print(f"💲 Price Range: ${min_price} - ${max_price}")
    print(f"🔄 Max Rounds: {max_rounds}, Threshold: {threshold:.1%}")
    print(f"📝 Logging to: {output}")
    print("=" * 60)
    
    agreement = False
    final_price = 0.0
    
    try:
        # Round 0: Buyer's opening offer
        print("🔵 Round 0: Buyer making opening offer...")
        buyer_offer = buyer.propose()
        logger.log({"round": 0, "role": "buyer", "offer": buyer_offer})
        print(f"Buyer offers: ${buyer_offer}")
        
        # Main negotiation loop
        for r in range(1, max_rounds + 1):
            print(f"\n🔴 Round {r}: Seller responding...")
            
            # Seller makes counteroffer
            seller_offer = seller.counter(buyer_offer)
            logger.log({"round": r, "role": "seller", "offer": seller_offer})
            print(f"Seller counteroffers: ${seller_offer}")
            
            # Check for convergence
            if buyer_offer > 0:  # Avoid division by zero
                price_diff = abs(seller_offer - buyer_offer)
                relative_diff = price_diff / buyer_offer
                
                if relative_diff < threshold:
                    final_price = (seller_offer + buyer_offer) / 2
                    agreement = True
                    print(f"✅ Agreement reached! Price difference ({price_diff:.2f}) is within threshold.")
                    print(f"💰 Final agreed price: ${final_price:.2f}")
                    break
            
            # Buyer responds if no agreement yet
            if r < max_rounds:  # Don't ask buyer to respond on the last round
                print(f"🔵 Round {r}: Buyer responding...")
                buyer_offer = buyer.respond(seller_offer)
                logger.log({"round": r, "role": "buyer", "offer": buyer_offer})
                print(f"Buyer counteroffers: ${buyer_offer}")
        
        # If no agreement after max rounds, call mediator
        if not agreement:
            print(f"\n🤝 No agreement after {max_rounds} rounds. Calling mediator...")
            final_price = mediator.suggest(buyer_offer, seller_offer)
            logger.log({"round": "mediator", "role": "mediator", "offer": final_price})
            print(f"Mediator suggests: ${final_price:.2f}")
        
        # Determine winner (who got closer to their ideal price)
        # Buyer wants low prices (closer to min_price), seller wants high prices (closer to max_price)
        buyer_distance = abs(final_price - min_price)
        seller_distance = abs(final_price - max_price)
        winner = "buyer" if buyer_distance < seller_distance else "seller"
        
        # Log final results
        logger.log({
            "final_price": final_price,
            "winner": winner,
            "agreement": agreement
        })
        
        print("=" * 60)
        print("📋 NEGOTIATION RESULTS:")
        print("=" * 60)
        print(f"💰 Final Price: ${final_price:.2f}")
        print(f"🏆 Winner: {winner.capitalize()}")
        print(f"🤝 Agreement Reached: {'Yes' if agreement else 'No (Mediated)'}")
        print(f"📊 Buyer's ideal (${min_price}) vs Seller's ideal (${max_price})")
        print("=" * 60)
        print(f"✅ Complete transcript saved to: {output}")
        
    except Exception as e:
        print(f"❌ Error during negotiation: {e}")
        # Retry once with a different seed
        try:
            print("🔄 Retrying with adjusted parameters...")
            run_negotiation(min_price, max_price, max_rounds, threshold, model, temp, seed + 1000, output)
        except Exception as retry_e:
            print(f"❌ Retry failed: {retry_e}")
            sys.exit(1)


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Buyer-Seller Negotiation Simulation")
    
    parser.add_argument("--min_price", type=float, default=config.MIN_PRICE,
                       help=f"Minimum price in negotiation range (default: {config.MIN_PRICE})")
    parser.add_argument("--max_price", type=float, default=config.MAX_PRICE,
                       help=f"Maximum price in negotiation range (default: {config.MAX_PRICE})")
    parser.add_argument("--max_rounds", type=int, default=config.MAX_ROUNDS,
                       help=f"Maximum negotiation rounds (default: {config.MAX_ROUNDS})")
    parser.add_argument("--threshold", type=float, default=config.CONVERGENCE_THRESHOLD,
                       help=f"Convergence threshold for agreement (default: {config.CONVERGENCE_THRESHOLD})")
    parser.add_argument("--model", type=str, default=config.DEFAULT_MODEL,
                       help=f"Ollama model to use (default: {config.DEFAULT_MODEL})")
    parser.add_argument("--temp", type=float, default=config.DEFAULT_TEMP,
                       help=f"Temperature for text generation (default: {config.DEFAULT_TEMP})")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED,
                       help=f"Random seed (default: {config.DEFAULT_SEED})")
    parser.add_argument("--output", type=str, default=config.DEFAULT_OUTPUT,
                       help=f"Output JSONL file (default: {config.DEFAULT_OUTPUT})")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.min_price <= 0:
        print("❌ Error: Minimum price must be positive")
        sys.exit(1)
    
    if args.max_price <= args.min_price:
        print("❌ Error: Maximum price must be greater than minimum price")
        sys.exit(1)
    
    if args.max_rounds < 1:
        print("❌ Error: Maximum rounds must be at least 1")
        sys.exit(1)
    
    if args.threshold <= 0 or args.threshold >= 1:
        print("❌ Error: Threshold must be between 0 and 1")
        sys.exit(1)
    
    if args.temp < 0 or args.temp > 2:
        print("❌ Error: Temperature must be between 0 and 2")
        sys.exit(1)
    
    # Run the negotiation
    run_negotiation(
        min_price=args.min_price,
        max_price=args.max_price,
        max_rounds=args.max_rounds,
        threshold=args.threshold,
        model=args.model,
        temp=args.temp,
        seed=args.seed,
        output=args.output
    )


if __name__ == "__main__":
    main() 