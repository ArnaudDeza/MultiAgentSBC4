# Buyer–Seller Negotiation Demo

A multi-agent system that simulates price negotiation between a buyer and seller, with an optional mediator to facilitate compromise when direct negotiation fails.

## Overview

This project demonstrates intelligent multi-agent negotiation where:
- A **BuyerAgent** tries to secure the lowest possible price
- A **SellerAgent** attempts to maximize their selling price  
- A **MediatorAgent** suggests fair compromises when parties can't reach agreement
- All offers and counteroffers are logged with timestamps for analysis

The system uses convergence thresholds to detect when parties are close enough to reach agreement, and includes robust price extraction from natural language responses.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have Ollama installed and running with the desired models:
```bash
ollama pull phi4
```

## Usage

### Basic Usage
```bash
python orchestrator.py
```

### Advanced Usage
```bash
python orchestrator.py \
  --min_price 100 \
  --max_price 300 \
  --max_rounds 5 \
  --threshold 0.05 \
  --model phi4 \
  --temp 0.6 \
  --seed 123 \
  --output demo_neg.jsonl
```

### Command Line Arguments

- `--min_price`: Minimum price in negotiation range (default: 50)
- `--max_price`: Maximum price in negotiation range (default: 200)
- `--max_rounds`: Maximum negotiation rounds (default: 5)
- `--threshold`: Convergence threshold for agreement as a fraction (default: 0.05 = 5%)
- `--model`: Ollama model to use (default: "phi4")
- `--temp`: Temperature for text generation (default: 0.7)
- `--seed`: Random seed for reproducibility (default: 42)
- `--output`: Output JSONL file path (default: "negotiation_log.jsonl")

## How It Works

### Negotiation Flow

1. **Opening Bid**: Buyer makes an initial offer
2. **Counteroffers**: Seller and buyer alternate making counteroffers
3. **Convergence Check**: After each round, the system checks if offers are within the threshold
4. **Agreement or Mediation**: Either parties agree, or a mediator suggests a compromise
5. **Winner Determination**: Based on who got closer to their ideal price

### Convergence Logic

Agreement is reached when:
```
|seller_offer - buyer_offer| / buyer_offer < threshold
```

For example, with a 5% threshold:
- Buyer offers $100, Seller offers $104 → 4% difference → Agreement!
- Buyer offers $100, Seller offers $110 → 10% difference → Continue negotiating

### Winner Determination

- **Buyer wins**: Final price is closer to the minimum price (buyer's ideal)
- **Seller wins**: Final price is closer to the maximum price (seller's ideal)

## Output Format

The system generates a JSONL file where each line contains a JSON object with these fields:

### During Negotiation
- `timestamp`: ISO timestamp when the record was created
- `round`: Round number (0 for opening bid, "mediator" for mediation)
- `role`: Agent role ("buyer", "seller", or "mediator") 
- `offer`: The price offered as a float

### Final Results
- `timestamp`: ISO timestamp
- `final_price`: The agreed or mediated final price
- `winner`: Either "buyer" or "seller"
- `agreement`: Boolean indicating if direct agreement was reached (vs mediation)

### Example Output Records

```json
{"timestamp": "2024-01-15T10:30:00.123456", "round": 0, "role": "buyer", "offer": 75.0}
{"timestamp": "2024-01-15T10:30:15.789012", "round": 1, "role": "seller", "offer": 150.0}
{"timestamp": "2024-01-15T10:30:30.345678", "round": 1, "role": "buyer", "offer": 85.0}
{"timestamp": "2024-01-15T10:30:45.901234", "round": 2, "role": "seller", "offer": 120.0}
{"timestamp": "2024-01-15T10:31:00.567890", "final_price": 102.5, "winner": "buyer", "agreement": true}
```

## Analysis and Visualization

After running a negotiation, you can analyze the results:

```python
import json
import matplotlib.pyplot as plt

# Load the negotiation log
with open('negotiation_log.jsonl', 'r') as f:
    records = [json.loads(line) for line in f]

# Extract offers by round
buyer_offers = [r['offer'] for r in records if r.get('role') == 'buyer']
seller_offers = [r['offer'] for r in records if r.get('role') == 'seller']

# Plot the negotiation progression
rounds = list(range(len(buyer_offers)))
plt.plot(rounds, buyer_offers, 'b-o', label='Buyer Offers')
plt.plot(range(1, len(seller_offers)+1), seller_offers, 'r-s', label='Seller Offers')
plt.xlabel('Round')
plt.ylabel('Price ($)')
plt.title('Negotiation Progress')
plt.legend()
plt.grid(True)
plt.show()
```

## Agent Strategies

### BuyerAgent
- Starts with offers closer to the minimum price
- Gradually increases offers but tries to stay below market middle
- Uses conservative movement toward seller's positions

### SellerAgent  
- Starts with offers closer to the maximum price
- Gradually decreases offers but tries to stay above market middle
- Responds strategically to buyer pressure

### MediatorAgent
- Analyzes both final positions objectively
- Suggests compromise prices when direct negotiation fails
- Aims for fair solutions that both parties might accept

## Error Handling

The system includes comprehensive error handling:
- **Price Extraction**: Robust parsing of natural language price responses
- **Fallback Logic**: Mathematical fallbacks when LLM responses are unclear  
- **Retry Mechanism**: Automatic retry with adjusted parameters on failure
- **Input Validation**: Thorough validation of all command-line arguments
- **Range Enforcement**: Ensures all offers stay within acceptable bounds

## Project Structure

- `config.py`: Configuration constants and negotiation parameters
- `utils.py`: JSON logging and timestamp utilities  
- `agents.py`: Agent class definitions (Buyer, Seller, Mediator)
- `orchestrator.py`: Main negotiation logic and CLI interface
- `ollama_utils.py`: Ollama API interaction utilities
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

## Customization

You can easily customize the negotiation by:

### Modifying Agent Behavior
```python
# In agents.py, adjust the prompts or fallback logic
def propose(self) -> float:
    prompt = f"As an aggressive buyer, make a very low opening bid..."
```

### Changing Negotiation Rules
```python
# In config.py, adjust the parameters
MAX_ROUNDS = 10          # Allow longer negotiations
CONVERGENCE_THRESHOLD = 0.02  # Require closer agreement (2%)
```

### Adding New Agent Types
```python
# Create specialized agents
class ConservativeBuyerAgent(BuyerAgent):
    def respond(self, seller_offer: float) -> float:
        # More conservative bidding strategy
        ...
```

## Tips for Effective Negotiations

1. **Lower threshold** = Requires closer agreement but may lead to more mediations
2. **Higher temperature** = More creative/unpredictable agent behavior
3. **More rounds** = Allows for more gradual convergence
4. **Wider price range** = Creates more room for strategic maneuvering

## Troubleshooting

**Problem**: Agents make offers outside the price range
- **Solution**: The system includes automatic range enforcement and fallback logic

**Problem**: No numeric prices extracted from responses  
- **Solution**: Multiple regex patterns and mathematical fallbacks handle this

**Problem**: Ollama connection issues
- **Solution**: Ensure Ollama is running and the specified model is available

**Problem**: No convergence after max rounds
- **Solution**: Adjust threshold or increase max_rounds; mediator will provide fallback 