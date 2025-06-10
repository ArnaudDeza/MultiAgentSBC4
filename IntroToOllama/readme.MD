# 🚀 Welcome to Your First AI Adventure with Ollama! 🚀

Hello, future AI pioneers! Welcome to your first hands-on experience with Large Language Models (LLMs). In this part of the bootcamp, you'll learn how to "talk" to an AI running right here on your own computer. We'll be using a cool tool called **Ollama**, which makes it easy to run powerful AI models locally.

Let's get started!

### Before You Begin: Is Your AI Ready?

Make sure you have Ollama running. You'll also need a model. For these first exercises, we recommend a smaller, friendly model. Let's pull one called `phi3`:

```bash
ollama pull phi3
```

Now you're all set to run your first AI programs!

---

## 📄 `HelloWorldOllama.py`: Your First Conversation with an AI

The first step in any friendship is a simple "hello." This script is your "hello world" for talking to an AI. Its purpose is to show you how to send a prompt (a question or a command) to an LLM and get a response back.

There are two fun ways to use this script.

### 1. Interactive Mode (The Easy Way)

If you just want to jump in and start chatting, run the script without any extra commands.

**Command:**
```bash
python3 HelloWorldOllama.py
```

**What Happens Next?**
1.  The program will first ask you to `Enter a prompt:`. You can type anything you want!
2.  Then, it will show you a list of all the AI models you have on your computer and ask you to pick one.
3.  The AI will think for a moment and then print its answer right in your terminal.

Your conversation is also automatically saved in a new text file inside the `IntroToOllama/results/HelloWorldOllama` folder, so you can always look back at it.

### 2. Direct Mode (For a Specific Question)

If you already know exactly what model you want to use and what you want to ask, you can tell the script everything in one go.

**Command:**
```bash
python3 HelloWorldOllama.py --model phi3 --prompt "In simple terms, what is a neural network?"
```

**What Happens Next?**
The script will immediately query the `phi3` model with your question and print the response. Just like before, the result is saved in the `results/HelloWorldOllama` folder.

---

## 🤖 `StructuredOutputOllama.py`: Teaching the AI to Follow Rules

Sometimes, you don't want a long, chatty paragraph from an AI. You might need a very specific, predictable answer, like "Yes," "No," or the letter "B" from a multiple-choice question. This is called **structured output**, and it's super important for building real-world AI applications.

This script shows you how to force the AI to answer in a clean JSON format that follows specific rules (we call these rules "schemas"). We've set up three examples for you.

### How to Run the Examples

You'll run the script with one argument to choose which example to run. You can also use the `--model` flag if you want to try a different AI.

#### Example 1: A Simple Yes or No

This example asks the AI a simple question and forces it to answer with only "Yes" or "No".

**Command:**
```bash
python3 StructuredOutputOllama.py yes_no
```

**Expected Output:**
You will see the prompt, then the AI's raw output (which is in a format called JSON), and finally the clean, validated answer.

```
--- Conversation ---
Prompt: Is Python a compiled language? Respond with either Yes or No.

--- Raw LLM Output ---
{
  "answer": "No"
}

--- Validated Response ---
answer='No'
----------------------
```

#### Example 2: A True or False Question

This example gives the AI a statement and forces it to decide if it's `true` or `false`.

**Command:**
```bash
python3 StructuredOutputOllama.py true_false
```

#### Example 3: A Multiple-Choice Question

Here, we give the AI a classic A/B/C/D question and force it to pick just one letter as its answer.

**Command:**
```bash
python3 StructuredOutputOllama.py abcd
```

For all these examples, the full conversation is saved in the `IntroToOllama/results/StructuredOutputOllama` folder. This is great for seeing exactly what the AI sent back and how our program understood it.

## 🎉 Now It's Your Turn!

Congratulations, you've successfully run a local LLM! Now the real fun begins. Go back to the Python files, see if you can understand what's happening, and try changing the prompts to ask your own questions!
