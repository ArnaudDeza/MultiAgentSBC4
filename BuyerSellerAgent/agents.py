"""Agent classes for the buyer-seller negotiation simulation."""

import re
from typing import Optional
from ollama_utils import ollama_query


def extract_price_from_response(response: str) -> Optional[float]:
    """Extract a numeric price from the LLM response.
    
    Args:
        response: The text response from the LLM
        
    Returns:
        The extracted price as a float, or None if no valid price found
    """
    # Look for patterns like "$100", "100.50", "$100.00", etc.
    patterns = [
        r'\$?(\d+\.?\d*)',  # $100, 100, 100.50
        r'(\d+\.?\d*)\s*dollars?',  # 100 dollars
        r'offer.*?(\d+\.?\d*)',  # offer 100
        r'bid.*?(\d+\.?\d*)',   # bid 100
        r'price.*?(\d+\.?\d*)',  # price 100
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None


class BuyerAgent:
    """Agent representing a buyer in the negotiation."""
    
    def __init__(self, model: str, temp: float, seed: int, min_price: float, max_price: float) -> None:
        """Initialize the BuyerAgent.
        
        Args:
            model: Ollama model name to use
            temp: Temperature setting for text generation
            seed: Random seed for reproducibility
            min_price: Minimum acceptable price range
            max_price: Maximum acceptable price range
        """
        self.model = model
        self.temp = temp
        self.seed = seed
        self.min_price = min_price
        self.max_price = max_price
    
    def propose(self) -> float:
        """Generate an opening bid.
        
        Returns:
            The proposed price as a float
        """
        prompt = f"As a buyer, propose an opening bid for an item. The acceptable price range is between ${self.min_price} and ${self.max_price}. As a buyer, you want to pay less. Give only a numeric dollar amount like '75' or '$75'."
        
        response = ollama_query(self.model, prompt, self.temp, self.seed)
        price = extract_price_from_response(response)
        
        # Fallback to a reasonable buyer's opening bid (closer to min_price)
        if price is None or price < self.min_price or price > self.max_price:
            price = self.min_price + (self.max_price - self.min_price) * 0.3
        
        return round(price, 2)
    
    def respond(self, seller_offer: float) -> float:
        """Respond to a seller's counteroffer.
        
        Args:
            seller_offer: The seller's counteroffer price
            
        Returns:
            The buyer's counteroffer price
        """
        prompt = f"As a buyer, the seller has offered ${seller_offer}. Make a counteroffer that's reasonable but still favors you as the buyer. The acceptable range is ${self.min_price} to ${self.max_price}. Give only a numeric dollar amount."
        
        response = ollama_query(self.model, prompt, self.temp, self.seed)
        price = extract_price_from_response(response)
        
        # Fallback: move halfway towards seller's offer but still favor buyer
        if price is None or price < self.min_price or price > self.max_price:
            # Move 30% of the way toward seller's offer from current position
            previous_position = self.min_price + (self.max_price - self.min_price) * 0.4
            price = previous_position + (seller_offer - previous_position) * 0.3
        
        return round(max(self.min_price, min(price, self.max_price)), 2)


class SellerAgent:
    """Agent representing a seller in the negotiation."""
    
    def __init__(self, model: str, temp: float, seed: int, min_price: float, max_price: float) -> None:
        """Initialize the SellerAgent.
        
        Args:
            model: Ollama model name to use
            temp: Temperature setting for text generation
            seed: Random seed for reproducibility
            min_price: Minimum acceptable price range
            max_price: Maximum acceptable price range
        """
        self.model = model
        self.temp = temp
        self.seed = seed
        self.min_price = min_price
        self.max_price = max_price
    
    def counter(self, buyer_offer: float) -> float:
        """Make a counteroffer to the buyer's offer.
        
        Args:
            buyer_offer: The buyer's offer price
            
        Returns:
            The seller's counteroffer price
        """
        prompt = f"As a seller, the buyer has offered ${buyer_offer}. Make a counteroffer that's reasonable but still favors you as the seller (you want to receive more money). The acceptable range is ${self.min_price} to ${self.max_price}. Give only a numeric dollar amount."
        
        response = ollama_query(self.model, prompt, self.temp, self.seed)
        price = extract_price_from_response(response)
        
        # Fallback: start high and move toward buyer's offer gradually
        if price is None or price < self.min_price or price > self.max_price:
            # Start closer to max_price and move 40% toward buyer's offer
            seller_position = self.max_price - (self.max_price - self.min_price) * 0.2
            price = seller_position - (seller_position - buyer_offer) * 0.4
        
        return round(max(self.min_price, min(price, self.max_price)), 2)


class MediatorAgent:
    """Agent that suggests compromise prices when direct negotiation fails."""
    
    def __init__(self, model: str, temp: float, seed: int) -> None:
        """Initialize the MediatorAgent.
        
        Args:
            model: Ollama model name to use
            temp: Temperature setting for text generation
            seed: Random seed for reproducibility
        """
        self.model = model
        self.temp = temp
        self.seed = seed
    
    def suggest(self, buyer_offer: float, seller_offer: float) -> float:
        """Suggest a fair compromise price.
        
        Args:
            buyer_offer: The buyer's final offer
            seller_offer: The seller's final offer
            
        Returns:
            A suggested compromise price
        """
        prompt = f"As a neutral mediator, the buyer's final offer is ${buyer_offer} and the seller's final offer is ${seller_offer}. Suggest a fair compromise price that both parties might accept. Give only a numeric dollar amount."
        
        response = ollama_query(self.model, prompt, self.temp, self.seed)
        price = extract_price_from_response(response)
        
        # Fallback: simple average of the two offers
        if price is None:
            price = (buyer_offer + seller_offer) / 2
        
        return round(price, 2) 