# Agentic AI Day at Seth Bonder Camp Level 4


## Part 1: Introduction to Ollama

Follow the readme.MD under the IntroTo Ollama. This will contain going over the 3 files:
    * HelloWorldOllama.py
    * StructuredOutputOllama.py
    * 


from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='qwen3:0.6b', messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)
    