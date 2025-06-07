"""
Agent classes for multi-agent debate system.
"""

import json
from typing import List, Dict, Any, Tuple
from ollama_utils import ollama_query, ollama_query_ABCD
from config import DEFAULT_NUM_CTX, DEFAULT_TOP_K, DEFAULT_TOP_P, DEFAULT_MIN_P, DEFAULT_REPEAT_PENALTY


class DebateAgent:
    """Agent that participates in debates using an LLM."""
    
    def __init__(self, agent_id: int, model: str, temp: float, seed: int) -> None:
        """
        Initialize debate agent.
        
        Args:
            agent_id: Unique identifier for this agent
            model: Ollama model name to use
            temp: Temperature for generation
            seed: Random seed for reproducibility
        """
        self.agent_id = agent_id
        self.model = model
        self.temp = temp
        self.seed = seed
        
    def respond(self, message: str) -> str:
        """
        Generate response to a message using the LLM.
        
        Args:
            message: Input prompt/message
            
        Returns:
            LLM response text
        """
        try:
            response = ollama_query(
                ollama_model=self.model,
                prompt_to_LLM=message,
                temperature=self.temp,
                seed=self.seed,
                num_ctx=DEFAULT_NUM_CTX,
                top_k=DEFAULT_TOP_K,
                top_p=DEFAULT_TOP_P,
                min_p=DEFAULT_MIN_P,
                repeat_penalty=DEFAULT_REPEAT_PENALTY
            )
            return response
        except Exception as e:
            print(f"Error in agent {self.agent_id} response: {e}")
            # Retry once
            try:
                response = ollama_query(
                    ollama_model=self.model,
                    prompt_to_LLM=message,
                    temperature=self.temp,
                    seed=self.seed + 1,  # Slightly different seed for retry
                    num_ctx=DEFAULT_NUM_CTX,
                    top_k=DEFAULT_TOP_K,
                    top_p=DEFAULT_TOP_P,
                    min_p=DEFAULT_MIN_P,
                    repeat_penalty=DEFAULT_REPEAT_PENALTY
                )
                return response
            except Exception as e2:
                print(f"Retry failed for agent {self.agent_id}: {e2}")
                return f"Agent {self.agent_id} encountered an error and cannot respond."


class JudgeAgent:
    """Agent that judges debate outcomes."""
    
    def __init__(self, model: str, temp: float, seed: int) -> None:
        """
        Initialize judge agent.
        
        Args:
            model: Ollama model name to use
            temp: Temperature for generation
            seed: Random seed for reproducibility
        """
        self.model = model
        self.temp = temp
        self.seed = seed
        
    def pick_winner(self, transcripts: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Analyze debate transcripts and pick a winner.
        
        Args:
            transcripts: List of debate log records
            
        Returns:
            Tuple of (winner_letter, justification)
        """
        # Extract final arguments from each agent
        agent_args = {}
        for record in transcripts:
            if 'agent' in record and 'message' in record:
                agent_id = record['agent']
                agent_args[agent_id] = record['message']
        
        # Build prompt for judge
        prompt_parts = ["Based on the following debate, which agent made the strongest case?"]
        
        agent_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i, (agent_id, message) in enumerate(sorted(agent_args.items())):
            letter = agent_letters[i] if i < len(agent_letters) else f"Agent{i}"
            prompt_parts.append(f"\n{letter} (Agent {agent_id}): {message}")
        
        prompt_parts.append(f"\nWhich agent ({'/'.join(agent_letters[:len(agent_args)])}) made the strongest case? Provide your answer as a single letter followed by a brief justification.")
        
        full_prompt = "".join(prompt_parts)
        
        try:
            response = ollama_query_ABCD(
                ollama_model=self.model,
                prompt=full_prompt,
                temperature=self.temp,
                seed=self.seed,
                num_ctx=DEFAULT_NUM_CTX,
                top_k=DEFAULT_TOP_K,
                top_p=DEFAULT_TOP_P,
                min_p=DEFAULT_MIN_P,
                repeat_penalty=DEFAULT_REPEAT_PENALTY
            )
            
            # Extract answer from structured response
            answer = response['message']['content']
            
            # Try to parse JSON response
            try:
                parsed = json.loads(answer)
                winner_letter = parsed.get('answer', 'Unknown')
            except json.JSONDecodeError:
                # Fallback: extract first letter
                winner_letter = answer.strip()[0] if answer.strip() else 'A'
            
            return winner_letter, answer
            
        except Exception as e:
            print(f"Error in judge decision: {e}")
            # Retry once
            try:
                response = ollama_query_ABCD(
                    ollama_model=self.model,
                    prompt=full_prompt,
                    temperature=self.temp,
                    seed=self.seed + 1,
                    num_ctx=DEFAULT_NUM_CTX,
                    top_k=DEFAULT_TOP_K,
                    top_p=DEFAULT_TOP_P,
                    min_p=DEFAULT_MIN_P,
                    repeat_penalty=DEFAULT_REPEAT_PENALTY
                )
                
                answer = response['message']['content']
                try:
                    parsed = json.loads(answer)
                    winner_letter = parsed.get('answer', 'Unknown')
                except json.JSONDecodeError:
                    winner_letter = answer.strip()[0] if answer.strip() else 'A'
                
                return winner_letter, answer
                
            except Exception as e2:
                print(f"Judge retry failed: {e2}")
                return 'A', "Judge encountered an error and defaulted to Agent A." 