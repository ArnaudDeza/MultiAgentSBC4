#!/usr/bin/env python3
import os
import argparse
import json
from datetime import datetime
from ollama import chat
from pydantic import BaseModel, ValidationError
from typing import Literal, Type, Optional


# ----------------------------
# 1. Pydantic Schemas for Structured Output
# ----------------------------
class YesNoResponse(BaseModel):
    """Schema for a Yes/No answer."""
    answer: Literal["Yes", "No"]


class TrueFalseResponse(BaseModel):
    """Schema for a True/False answer."""
    answer: bool


class MultipleChoiceResponse(BaseModel):
    """Schema for a multiple-choice answer (A/B/C/D)."""
    answer: Literal["A", "B", "C", "D"]


def ollama_query_structured(
    model: str,
    prompt: str,
    schema: Type[BaseModel],
    temperature: float = 0.0,
):
    """
    Queries the Ollama model and expects a JSON response that conforms to the
    provided Pydantic schema.
    Returns a tuple of (raw_response_string, Optional[BaseModel]).
    """
    system_prompt = f"""
    You must respond in a valid JSON format.
    The JSON object must strictly adhere to the following Pydantic schema:
    {schema.model_json_schema()}
    """
    
    response_content = None
    try:
        response = chat(
            model=model,
            options={"temperature": temperature},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            format="json",  # This is crucial for structured output
        )

        response_content = response["message"]["content"]
        
        validated_response = schema.model_validate_json(response_content)
        return response_content, validated_response

    except ValidationError:
        # Return raw content for logging, but None for validated object
        return response_content, None
    except Exception as e:
        print(f"An unexpected error occurred during the Ollama API call: {e}")
        return None, None


def save_response(
    model: str,
    example_name: str,
    prompt: str,
    raw_response: str,
    validated_response: Optional[BaseModel],
):
    """Saves the prompt, raw response, and validated data to a file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(current_dir, "results", "StructuredOutputOllama")
    os.makedirs(results_dir, exist_ok=True)

    safe_model_name = model.replace("/", "_").replace(":", "-")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(
        results_dir, f"{example_name}_{safe_model_name}_{timestamp}.txt"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write("--- Prompt ---\n")
        f.write(f"Model: {model}\n")
        f.write(f"Example: {example_name}\n\n")
        f.write(f"{prompt.strip()}\n\n")

        f.write("--- Raw LLM Output ---\n")
        f.write(f"{raw_response}\n\n")

        f.write("--- Validated Response ---\n")
        if validated_response:
            f.write(validated_response.model_dump_json(indent=2))
        else:
            f.write("Validation Failed.")
        f.write("\n")

    print(f"Conversation saved to {filename}")


def process_and_display_response(
    model: str,
    example_name: str,
    prompt: str,
    schema: Type[BaseModel],
):
    """Helper to query, print, and save the structured output response."""
    raw_response, validated_response = ollama_query_structured(
        model, prompt, schema
    )

    print("\n--- Conversation ---")
    print(f"Prompt: {prompt.strip()}")
    print("\n--- Raw LLM Output ---")
    print(raw_response)
    
    if validated_response:
        print("\n--- Validated Response ---")
        print(validated_response)
    else:
        print("\n--- Validation Failed ---")
        if raw_response is not None:
             print(f"The model output could not be validated against the {schema.__name__} schema.")
    
    print("----------------------\n")

    if raw_response is not None:
        save_response(
            model=model,
            example_name=example_name,
            prompt=prompt,
            raw_response=raw_response,
            validated_response=validated_response,
        )


# ----------------------------
# Example Runners
# ----------------------------

def run_example_yes_no(model: str):
    """Runs the Yes/No example."""
    print(f"\n--- Running Yes/No Example with model: {model} ---")
    prompt = "Is Python a compiled language? Respond with either Yes or No."
    process_and_display_response(model, "yes_no", prompt, YesNoResponse)


def run_example_true_false(model: str):
    """Runs the True/False example."""
    print(f"\n--- Running True/False Example with model: {model} ---")
    prompt = "The Eiffel Tower is located in Berlin. True or False?"
    process_and_display_response(model, "true_false", prompt, TrueFalseResponse)


def run_example_abcd(model: str):
    """Runs the A/B/C/D multiple-choice example."""
    print(f"\n--- Running Multiple-Choice Example with model: {model} ---")
    prompt = """
What is the primary function of a CPU in a computer?
A) Store data long-term
B) Execute instructions and perform calculations
C) Display images on the monitor
D) Connect to the internet
"""
    process_and_display_response(model, "abcd", prompt, MultipleChoiceResponse)


def main():
    """Main function to run the structured output examples."""
    parser = argparse.ArgumentParser(
        description="Run structured output examples with Ollama.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "example",
        choices=["yes_no", "true_false", "abcd"],
        help=(
            "The example to run:\n"
            "  - yes_no: A question expecting a 'Yes' or 'No' answer.\n"
            "  - true_false: A statement expecting a 'True' or 'False' answer.\n"
            "  - abcd: A multiple-choice question expecting 'A', 'B', 'C', or 'D'."
        ),
    )
    parser.add_argument(
        "--model",
        type=str,
        default="phi4:latest",
        help="The Ollama model to use (default: phi4:latest).",
    )
    args = parser.parse_args()

    # Dynamically call the appropriate example function
    example_func_name = f"run_example_{args.example}"
    example_func = globals().get(example_func_name)
    
    if example_func:
        example_func(args.model)
    else:
        print(f"Error: Example function '{example_func_name}' not found.")


if __name__ == "__main__":
    main()
