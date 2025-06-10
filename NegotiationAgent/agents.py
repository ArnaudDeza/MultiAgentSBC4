"""
Agent classes for the multi-agent negotiation system.
"""
import re
from ollama_utils import ollama_query
from prompts import BUYER_PROMPT, SELLER_PROMPT, MODERATOR_PROMPT

class Agent:
    """Base class for all negotiation agents."""
    def __init__(self, model: str, temp: float, seed: int):
        self.model = model
        self.temp = temp
        self.seed = seed

    def _query_llm(self, prompt: str) -> str:
        """Helper to query the LLM with simple retry logic."""
        try:
            return ollama_query(self.model, prompt, self.temp, self.seed)
        except Exception as e:
            print(f"Error querying model {self.model}: {e}. Retrying...")
            try:
                return ollama_query(self.model, prompt, self.temp, self.seed + 1)
            except Exception as e2:
                print(f"Retry failed for {self.model}: {e2}")
                return "Agent encountered an error."

    def parse_price(self, response: str) -> (float, str):
        """Extracts the price from the agent's response text."""
        price_match = re.search(r"Price: \$?(\d+\.?\d*)", response, re.IGNORECASE)
        if price_match:
            price = float(price_match.group(1))
            # Clean the response by removing the price line
            cleaned_response = response[:price_match.start()].strip()
            return price, cleaned_response
        return None, response # Return the original response if no price is found

class SellerAgent(Agent):
    """Represents the Seller in the negotiation."""
    def __init__(self, model: str, temp: float, seed: int, scenario: dict):
        super().__init__(model, temp, seed)
        self.scenario = scenario

    def act(self, chat_history: str) -> (float, str):
        prompt = SELLER_PROMPT.format(
            scenario_name=self.scenario['name'],
            item_name=self.scenario['item_name'],
            list_price=self.scenario['list_price'],
            min_price=self.scenario['seller_min_price'],
            personality=self.scenario['seller_personality'],
            chat_history=chat_history
        )
        response = self._query_llm(prompt)
        return self.parse_price(response)

class BuyerAgent(Agent):
    """Represents the Buyer in the negotiation."""
    def __init__(self, model: str, temp: float, seed: int, scenario: dict):
        super().__init__(model, temp, seed)
        self.scenario = scenario

    def act(self, chat_history: str) -> (float, str):
        prompt = BUYER_PROMPT.format(
            scenario_name=self.scenario['name'],
            item_name=self.scenario['item_name'],
            list_price=self.scenario['list_price'],
            target_price=self.scenario['buyer_target_price'],
            max_price=self.scenario['buyer_max_price'],
            desire_level=self.scenario['buyer_desire_level'],
            chat_history=chat_history
        )
        response = self._query_llm(prompt)
        return self.parse_price(response)

class ModeratorAgent(Agent):
    """Analyzes the finished negotiation."""
    def analyze(self, transcript: str, final_price: float, scenario: dict) -> str:
        prompt = MODERATOR_PROMPT.format(
            item_name=scenario['item_name'],
            final_price=final_price,
            seller_min_price=scenario['seller_min_price'],
            buyer_target_price=scenario['buyer_target_price'],
            buyer_max_price=scenario['buyer_max_price'],
            transcript=transcript
        )
        return self._query_llm(prompt) 