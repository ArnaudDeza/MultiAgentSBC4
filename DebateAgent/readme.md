# Technical Documentation: Multi-Agent Debate System

This document provides a detailed technical explanation of how the multi-agent debate system works, including the debate mechanics, judging system, and architectural decisions.

## Code Architecture & Flow

### 1. System Components

The system is built with a modular architecture consisting of five main components:

#### `ollama_utils.py` - LLM Interface Layer
- **Purpose**: Abstracts Ollama API interactions with error handling and retry logic
- **Key Functions**:
  - `ollama_query()`: General text generation with configurable parameters
  - `ollama_query_ABCD()`: Structured responses for multiple-choice scenarios (used by judges)
  - `ollama_query_Yes_No()`: Binary choice responses
- **Why**: Centralized LLM interaction prevents code duplication and provides consistent error handling

#### `config.py` - Configuration Management
- **Purpose**: Centralized configuration for models, hyperparameters, and defaults
- **Key Elements**:
  - `OLLAMA_NICKNAMES`: Maps full model names to readable aliases
  - Default values for agents, rounds, temperature, etc.
  - Ollama-specific parameters (context length, top-k, top-p)
- **Why**: Separation of configuration from logic allows easy tuning without code changes

#### `utils.py` - Utility Functions
- **Purpose**: Provides logging and timestamp functionality
- **JsonLogger Class**: 
  - Automatically adds ISO-8601 timestamps to all log entries
  - Appends to JSONL files for streaming analysis
  - Thread-safe file operations
- **Why**: JSONL format enables real-time monitoring and post-processing analysis

#### `agents.py` - Agent Implementations
- **DebateAgent**: Individual debate participants
- **JudgeAgent**: Evaluates debates and determines winners
- **Why Separate Classes**: Different agents have different responsibilities and prompt structures

#### `orchestrator.py` - Main Control Logic
- **Purpose**: Coordinates the entire debate process
- **Responsibilities**: CLI parsing, agent lifecycle, round management, result aggregation

### 2. Debate Flow Mechanics

#### Phase 1: Initialization
```python
# Each agent gets a unique seed for diversity
agents = [DebateAgent(i, model, temp, seed + i) for i in range(num_agents)]
```
- **Seed Strategy**: Base seed + agent_id ensures reproducible but diverse responses
- **Agent Independence**: Each agent maintains its own conversation context

#### Phase 2: Opening Statements
```python
prompt = f"Please introduce your position on this topic: {topic}"
```
- **No Prior Context**: Agents start with clean slate, develop independent positions
- **Logging**: Each statement logged with `type: "opening_statement"` for analysis

#### Phase 3: Iterative Debate Rounds
```python
# Gather latest responses from OTHER agents
other_agents_latest = {}
for record in reversed(current_transcripts):
    if record['agent'] != current_agent_id:
        other_agents_latest[record['agent']] = record['message']
```

**Key Design Decisions**:
- **Recency Bias**: Agents only see the most recent message from each other agent
- **No Self-Reference**: Agents don't see their own previous messages in context
- **Dynamic Context**: Context builds as debate progresses

#### Phase 4: Judgment
```python
judge = JudgeAgent(model, temp, seed + 1000)  # Different seed for impartiality
winner_letter, justification = judge.pick_winner(transcripts)
```
- **Separate Judge Instance**: Uses different seed to avoid bias toward any particular agent
- **Full Transcript Analysis**: Judge sees complete debate history, not just latest messages

## Judge Implementation Deep Dive

### How Judges Work

The `JudgeAgent` implements a sophisticated evaluation system:

#### 1. Transcript Processing
```python
# Extract final arguments from each agent
agent_args = {}
for record in transcripts:
    if 'agent' in record and 'message' in record:
        agent_id = record['agent']
        agent_args[agent_id] = record['message']  # Most recent overwrites
```
- **Latest Argument Focus**: Judge evaluates agents based on their most recent (strongest) arguments
- **Equal Representation**: Each agent gets exactly one argument presented to the judge

#### 2. Structured Prompt Generation
```python
agent_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
for i, (agent_id, message) in enumerate(sorted(agent_args.items())):
    letter = agent_letters[i]
    prompt_parts.append(f"\n{letter} (Agent {agent_id}): {message}")
```
- **Anonymization**: Agents presented as letters (A, B, C) to reduce numeric bias
- **Consistent Ordering**: `sorted()` ensures deterministic agent presentation

#### 3. Structured Response Parsing
The judge uses the `ollama_query_ABCD()` function which enforces a specific response format:
```python
response = ollama_query_ABCD(model, prompt, ...)
# Returns structured JSON: {"answer": "A", "justification": "..."}
```

### Why This Judge Design?

1. **Impartiality**: Separate judge instance with different seed prevents alignment with any agent
2. **Structured Evaluation**: Multiple-choice format forces clear decisions
3. **Transparency**: Justification requirement provides reasoning for decisions
4. **Consistency**: Same evaluation criteria applied across all debates

## Pydantic Integration & Purpose

### Why We Use Pydantic

Pydantic serves a crucial role in ensuring reliable, structured responses from LLMs:

#### 1. Response Schema Enforcement
```python
class MultipleChoiceResponse(BaseModel):
    answer: Literal["A", "B", "C", "D"]
```
- **Type Safety**: Ensures judge responses are always valid letters
- **Format Consistency**: Prevents free-form responses that are hard to parse
- **Validation**: Automatic validation of LLM outputs

#### 2. JSON Schema Generation
```python
format=MultipleChoiceResponse.model_json_schema()
```
- **Ollama Integration**: Pydantic schemas are passed to Ollama to constrain generation
- **Structured Generation**: LLM is forced to produce valid JSON matching the schema
- **Error Reduction**: Eliminates parsing errors from malformed responses

#### 3. Alternative Response Types
The system includes multiple Pydantic models for different use cases:
```python
class YesNoResponse(BaseModel):
    answer: Literal["Yes", "No"]

class TrueFalseResponse(BaseModel):
    answer: Literal["True", "False"]
```

### Without Pydantic: The Problems

1. **Parsing Failures**: LLMs might respond with "I choose A because..." instead of just "A"
2. **Inconsistent Formats**: Responses like "Agent A", "Option A", "A)", "a" all mean the same thing
3. **Extraction Complexity**: Complex regex/parsing logic needed to extract decisions
4. **Error Handling**: Need fallback logic for unparseable responses

### With Pydantic: The Benefits

1. **Guaranteed Format**: Always get `{"answer": "A"}` or similar valid JSON
2. **Type Safety**: Python type system can rely on response structure
3. **Automatic Validation**: Pydantic rejects invalid responses before they reach our code
4. **Self-Documenting**: Schema serves as documentation for expected response format

## Advanced Features & Design Patterns

### Error Handling Strategy

#### Agent-Level Resilience
```python
try:
    response = ollama_query(...)
except Exception as e:
    # Retry with modified seed
    response = ollama_query(..., seed=seed + 1)
```
- **Graceful Degradation**: Agents continue functioning even if individual queries fail
- **Seed Variation**: Retry uses slightly different seed to avoid repeated failures
- **Fallback Messages**: Clear error messages when all retries fail

#### Judge-Level Resilience
```python
try:
    parsed = json.loads(answer)
    winner_letter = parsed.get('answer', 'Unknown')
except json.JSONDecodeError:
    # Fallback: extract first letter
    winner_letter = answer.strip()[0] if answer.strip() else 'A'
```
- **Multiple Parsing Strategies**: JSON parsing with character fallback
- **Default Decisions**: System always produces a decision, even on failures

### Logging Strategy

#### Structured Logging Format
```python
{
    "timestamp": "2024-01-15T10:30:00.000000",
    "round": 1,
    "agent": 0,
    "message": "...",
    "type": "debate_response"
}
```
- **Searchable**: Each field can be filtered/queried independently
- **Temporal**: Timestamps enable timeline analysis
- **Typed**: `type` field allows filtering by event type
- **Streaming**: JSONL format supports real-time analysis

#### Analysis Capabilities
The logging format enables:
- **Argument Evolution**: Track how positions change over rounds
- **Agent Performance**: Compare argument quality across agents
- **Topic Analysis**: Study how different topics affect debate dynamics
- **Model Comparison**: Compare different LLM behaviors

### Scalability Considerations

#### Memory Management
- **Stateless Agents**: Agents don't store conversation history internally
- **Lazy Loading**: Transcripts loaded from disk only when needed
- **Configurable Context**: `num_ctx` parameter controls memory usage

#### Extensibility
- **Plugin Architecture**: New agent types can inherit from base classes
- **Model Agnostic**: System works with any Ollama-compatible model
- **Flexible Judging**: Judge criteria can be modified without changing core logic

## Performance Characteristics

### Time Complexity
- **Sequential Processing**: O(agents × rounds) LLM calls for debate
- **Transcript Loading**: O(total_messages) for judge analysis
- **Bottleneck**: LLM generation speed, not system logic

### Space Complexity
- **Log Growth**: O(agents × rounds × message_length) disk space
- **Memory Usage**: Minimal - only current round data in memory
- **Scalability**: Can handle large debates limited only by disk space

This architecture provides a robust, extensible foundation for multi-agent debates while maintaining simplicity and reliability.
