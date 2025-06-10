# Multi-Agent Debate System

Welcome to the Multi-Agent Debate System! This project is a fun, hands-on introduction to the world of agentic AI, designed for the GenAI summer boot camp. Here, you'll get to orchestrate a debate between multiple Large Language Model (LLM) agents on various fun and thought-provoking topics.

## 🚀 Educational Goals

This project is designed to give you practical experience with several key concepts in AI:

-   **Agentic AI**: You'll see how we can give AI agents specific roles (Debate Agent, Judge) and goals, and have them interact to complete a complex task.
-   **Prompt Engineering**: The quality of an LLM's response depends heavily on the quality of its prompt. You'll learn how to craft effective prompts to guide the agents' behavior. You can even modify the prompts in `DebateAgent/prompts.py` to see how it changes the debate!
-   **LLM Interaction**: You'll use the `ollama` library to have your Python code communicate with powerful local LLMs.
-   **Parsing LLM Output**: LLMs produce unstructured text. We'll use simple but effective techniques (like regular expressions) to parse the judge's final verdict and extract structured data from it.

---

## 📂 Codebase Overview

The project is structured to be as clear as possible. Here are the main files you'll interact with:

-   `DebateAgent/orchestrator.py`: This is the heart of the project. It's the main script you'll run to start and manage the debate. It handles getting your settings, running the debate rounds, and saving the results.
-   `DebateAgent/agents.py`: This file defines the `DebateAgent` and `JudgeAgent` classes. It contains the logic for how an agent responds to a prompt and how the judge decides the winner.
-   `DebateAgent/prompts.py`: All the prompts for the agents and the judge are stored here as string templates. This is the best place to start if you want to experiment with changing the agents' behavior!
-   `DebateAgent/topics.py`: This file contains the list of pre-defined debate topics. Feel free to add your own!
-   `DebateAgent/ollama_utils.py`: A small helper file that contains the function for sending a prompt to an Ollama model and getting a response.
-   `DebateAgent/produce_debate_audio.py`: A utility script to turn a finished debate transcript into an MP3 audio file.

---

## ⚙️ How to Use

Follow these steps to set up and run your first AI debate.

### 1. Prerequisites

-   **Ollama**: Make sure you have [Ollama](https://ollama.com/) installed and running.
-   **LLM Models**: You need at least one model installed in Ollama. We recommend starting with a smaller, faster model. You can install one by running:
    ```bash
    ollama pull phi3
    ```
-   **Python Libraries**: You'll need the `gTTS` library to generate the audio file. Install it using pip:
    ```bash
    pip install gTTS
    ```

### 2. Running a Debate

To start a debate, run the `orchestrator.py` script from your terminal:

```bash
python DebateAgent/orchestrator.py
```

The script will guide you through an interactive setup process:

1.  **Choose a Topic**: You'll be shown a list of topics and asked to choose one.
2.  **Set Number of Agents**: Decide how many agents will participate (minimum of 2).
3.  **Set Number of Rounds**: Choose how many rounds the debate will last.
4.  **Configure Agents**: For each agent, you will specify:
    -   The **Ollama model** they should use.
    -   Their **stance** on the topic (e.g., "For", "Against", "Skeptical").
5.  **Configure Judge**: Choose the Ollama model for the judge.

Once configured, the debate will start, and you'll see the agents' responses printed to the console in real-time.

### 3. Viewing the Results

After the debate concludes, a new folder is created in the `DebateAgent/results` directory. The folder name will be timestamped and contain details about the debate. Inside, you'll find two files:

-   `transcript.jsonl`: A JSONL file where every line is a JSON object representing an event in the debate (a message from an agent, the final verdict, etc.).
-   `metadata.json`: A single JSON file containing all the configuration details of the debate, timing information, and the final results.

### 4. Generating the Audio File

Want to listen to your debate? Use the `produce_debate_audio.py` script. Run it from the terminal and provide the path to the results folder you want to narrate.

**Example:**

```bash
python DebateAgent/produce_debate_audio.py DebateAgent/results/your_debate_results_folder_name
```

This will create a `debate_audio.mp3` file inside that same results folder. Enjoy the show! 