#!/usr/bin/env python3
import os
import argparse
from datetime import datetime
from ollama import list as ollama_list, chat


def ollama_query(
    ollama_model: str,
    prompt_to_LLM: str,
    temperature: float,
    seed: int = 0,
    num_ctx: int = 4096,
    top_k: int = 40,
    top_p: float = 0.9,
    min_p: float = 0.05,
    repeat_penalty: float = 1.1,
):
    """
    Simple wrapper around Ollama chat API.
    See:
    - https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options
    - https://github.com/ollama/ollama/blob/main/docs/modelfile.md
    """
    response = chat(
        model=ollama_model,
        options={
            "temperature": temperature,
            "seed": seed,
            "num_ctx": num_ctx,
            "top_k": top_k,
            "top_p": top_p,
            "min_p": min_p,
            "repeat_penalty": repeat_penalty,
        },
        messages=[{"role": "user", "content": prompt_to_LLM}],
    )
    return response["message"]["content"]


def save_response(model, prompt, response):
    """Saves the response to a file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(current_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    safe_model_name = model.replace("/", "_").replace(":", "-")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(results_dir, f"{safe_model_name}_{timestamp}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Model: {model}\n")
        f.write(f"Prompt:\n{prompt}\n\nResponse:\n{response}\n")

    print(f"Response saved to {filename}")


def run_single_query(model, prompt):
    """Runs a single query, prints the response, and saves it to a file."""
    print(f"\nQuerying model '{model}' with prompt: '{prompt}'")
    try:
        response = ollama_query(model, prompt, temperature=0.7)
        print("\n--- Response ---")
        print(response)
        print("--- End Response ---\n")
        save_response(model, prompt, response)
    except Exception as err:
        print(f"Error querying model {model}: {err}")


def run_interactive_mode():
    """Guides the user to select a model and provide a prompt."""
    prompt = input("Enter a prompt: ")

    try:
        models_info = ollama_list()
        # The ollama library returns a dictionary with a 'models' key
        # which contains a list of model details.
        print(models_info)
        models = [m["model"] for m in models_info["models"]]
    except Exception as e:
        print(f"Failed to list models from Ollama: {e}")
        return

    if not models:
        print(
            "No Ollama models found. "
            "Please make sure Ollama is running and you have pulled some models."
        )
        return

    print("\nAvailable models:")
    for i, model_name in enumerate(models):
        print(f"  {i + 1}: {model_name}")

    while True:
        try:
            choice = input(f"Select a model (1-{len(models)}): ")
            model_index = int(choice) - 1
            if 0 <= model_index < len(models):
                selected_model = models[model_index]
                break
            else:
                print("Invalid selection. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    run_single_query(selected_model, prompt)


def main():
    """Main function to run the script from the command line."""
    parser = argparse.ArgumentParser(
        description="A script to query Ollama models in two ways:\n"
        "1. Direct: Provide a model and prompt as arguments.\n"
        "   Example: python HelloWorldOllama.py --model llama2 --prompt 'Why is the sky blue?'\n"
        "2. Interactive: Run without arguments to be prompted for input.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--model", type=str, help="The name of the model to use (e.g., 'llama2')."
    )
    parser.add_argument(
        "--prompt", type=str, help="The prompt to send to the model."
    )
    args = parser.parse_args()

    if args.model and args.prompt:
        run_single_query(args.model, args.prompt)
    else:
        run_interactive_mode()


if __name__ == "__main__":
    main()
