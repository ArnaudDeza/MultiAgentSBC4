# Multi-Agent AI Negotiation Simulator

Welcome to the Negotiation Simulator! This project provides a fun, interactive way to explore agentic AI by simulating a negotiation between a buyer and a seller, each with their own secret goals.

## 🚀 Educational Goals

This simulation is designed to be a learning tool that demonstrates several key concepts in AI:

-   **Goal-Oriented Agents**: Unlike a simple chatbot, the Buyer and Seller agents have specific, hidden objectives (a minimum or maximum price) that guide their behavior.
-   **Hidden Information**: A core concept in game theory and AI. The agents must interact and reason without knowing the other's secret goals, just like in a real negotiation.
-   **Persona-Driven Prompts**: The prompts in `prompts.py` not only give the agents their goals but also a `personality` or `desire_level`, showing how you can influence the *style* of an LLM's response.
-   **Structured Output Parsing**: The orchestrator needs to "understand" the negotiation by parsing the price from the agents' natural language responses using regular expressions.

---

## 📂 Codebase Overview

-   `orchestrator.py`: The main script you run to start the negotiation simulation.
-   `agents.py`: Defines the `BuyerAgent`, `SellerAgent`, and `ModeratorAgent` classes.
-   `prompts.py`: Contains the core prompts that give the agents their secret instructions and personalities. This is the best place to experiment!
-   `scenarios.py`: A dictionary of pre-defined negotiation settings, including items, list prices, and the secret goals for each agent.
-   `visualize_negotiation.py`: A script to generate a beautiful HTML chat visualization of the negotiation.
-   `produce_negotiation_audio.py`: A script to create an MP3 audio narration of the negotiation.
-   `config.py` & `ollama_utils.py`: Helper files for configuring and running Ollama models.

---

## ⚙️ How to Use

### 1. Prerequisites

-   **Ollama**: Ensure [Ollama](https://ollama.com/) is installed and running on your machine.
-   **LLM Models**: Install at least one model. `phi3` is a good, fast choice.
    ```bash
    ollama pull phi3
    ```
-   **Python Libraries**: Install `gTTS` to enable the audio generation feature.
    ```bash
    pip install gTTS
    ```

### 2. Running the Simulation

To start a negotiation, run the `orchestrator.py` script from your terminal:

```bash
python NegotiationAgent/orchestrator.py
```

The script will then guide you through the setup:

1.  **Choose a Scenario**: Pick a negotiation setting like a yard sale or a fish market.
2.  **Set Negotiation Rounds**: Decide the maximum number of back-and-forth turns.
3.  **Select Models**: Choose the Ollama models for the Buyer, Seller, and Moderator.

The negotiation will then play out in your terminal.

### 3. Viewing the Results

After the simulation, a new, timestamped folder is created in `NegotiationAgent/results/`. Inside, you will find:

-   `transcript.jsonl`: The raw log of every turn in the negotiation.
-   `metadata.json`: The configuration and final outcome (Deal or No Deal).
-   `summary.md`: The Moderator's expert analysis of who won the negotiation and why.

### 4. Visualizing the Negotiation

To view the negotiation in a chat-style interface, run the visualization script on your results folder:

```bash
python NegotiationAgent/visualize_negotiation.py NegotiationAgent/results/your_results_folder_name
```

This creates a `negotiation_visualization.html` file in the folder. Open it in any web browser.

### 5. Listening to the Negotiation

To generate an audio narration of the haggling, run the audio script:

```bash
python NegotiationAgent/produce_negotiation_audio.py NegotiationAgent/results/your_results_folder_name
```

This creates a `negotiation_audio.mp3` file in the results folder. 