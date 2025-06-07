from ollama import ListResponse, list
from ollama import chat
from pydantic import BaseModel
from typing import Literal


OLLAMA_NICKNAMES= {
        "gemma3:12b": "gemma3_12b",
        "phi4": "phi4",
        "qwq": "qwq",
        "llama3.3": "llama3_3",
        "phi4-mini": "phi4_mini",
}



def get_available_models():
    """
    Get the list of models available in the Ollama server.
    
    Returns:
        List[str]: List of model names
    """
    try:
        response: ListResponse = list()
        return [model.model for model in response.models]
    except Exception as e:
        print(f"Error getting available models: {e}")
        return []


def print_ollama_models():
    """
    Print the list of models available in the Ollama server.
    """
    response: ListResponse = list()

    for model in response.models:
        print('Name:', model.model)
        print('  Size (MB):', f'{(model.size.real / 1024 / 1024):.2f}')
        if model.details:
            print('  Format:', model.details.format)
            print('  Family:', model.details.family)
            print('  Parameter Size:', model.details.parameter_size)
            print('  Quantization Level:', model.details.quantization_level)
        print('\n')


def ollama_query(ollama_model: str,
                 prompt_to_LLM: str,
                 temperature: float,
                 seed: int = 0,
                 num_ctx: int = 4096,
                 top_k: int = 40,
                 top_p: float = 0.9,
                 min_p: float = 0.05,
                 repeat_penalty: float = 1.1,
                 ) -> str:
    """
    See https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options
    and https://github.com/ollama/ollama/blob/main/docs/modelfile.md for explanations
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
                 "repeat_penalty": repeat_penalty
                 },
            messages=[
                {
                    'role': 'user',
                    'content': prompt_to_LLM
                }
            ]
        )
    ret = response['message']['content']
    return ret


# ----------------------------
# 1. Yes/No schema
# ----------------------------
class YesNoResponse(BaseModel):
    answer: Literal["Yes", "No"]

# ----------------------------
# 2. True/False schema
# ----------------------------
class TrueFalseResponse(BaseModel):
    answer: Literal["True", "False"]

# ----------------------------
# 3. Multiple-Choice (A/B/C/D) schema
# ----------------------------
class MultipleChoiceResponse(BaseModel):
    answer: Literal["A", "B", "C", "D"]

def ollama_query_Yes_No(ollama_model: str, prompt: str, temperature: float, seed: int = 0,
                 num_ctx: int = 4096,
                 top_k: int = 40,
                 top_p: float = 0.9,
                 min_p: float = 0.05,
                 repeat_penalty: float = 1.1,
                 ):
   
    response = chat(
            model=ollama_model,
            options={
                "temperature": temperature,
                 "seed": seed,
                 "num_ctx": num_ctx,
                 "top_k": top_k,
                 "top_p": top_p,
                 "min_p": min_p,
                 "repeat_penalty": repeat_penalty
                 },
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            format=YesNoResponse.model_json_schema(),
        ) 
    return response

def ollama_query_ABCD(ollama_model: str, prompt: str, temperature: float, seed: int = 0,
                 num_ctx: int = 4096,
                 top_k: int = 40,
                 top_p: float = 0.9,
                 min_p: float = 0.05,
                 repeat_penalty: float = 1.1
                 ):
   
    response = chat(
            model=ollama_model,
            options={
                "temperature": temperature,
                 "seed": seed,
                 "num_ctx": num_ctx,
                 "top_k": top_k,
                 "top_p": top_p,
                 "min_p": min_p,
                 "repeat_penalty": repeat_penalty
                 },
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            format=MultipleChoiceResponse.model_json_schema(),
        ) 
    return response


if __name__ == '__main__':
    print_ollama_models()
    
    # Simple test example: Say hello to phi4 model
    print("=" * 50)
    print("Testing phi4 model with a simple hello message:")
    print("=" * 50)
    
    try:
        response = ollama_query(
            ollama_model="phi4",
            prompt_to_LLM="Hello! Please introduce yourself briefly.",
            temperature=0.7,
            seed=42
        )
        print(f"phi4 response: {response}")
    except Exception as e:
        print(f"Error querying phi4 model: {e}")
        print("Make sure the phi4 model is installed in Ollama. You can install it with: ollama pull phi4") 