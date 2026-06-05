# Weekly Task Submission: ChatAgent Implementation

**Author:** Gurjot Singh

## Overview
This submission contains the implementation of a terminal-based conversational AI, structured around a model-agnostic `ChatAgent` class. The chatbot interacts with various Large Language Models via the OpenRouter API, leveraging the official `openai` Python SDK. It is designed to handle multi-turn conversations efficiently while strictly adhering to memory and context constraints.

## Architecture & Design Decisions

### 1. Object-Oriented State Management
Instead of relying on global variables, the application logic is written within the `ChatAgent` class. This allows for clean instantiation of the agent with distinct configurations—specifically the underlying model, the system prompt, and the maximum turn threshold.

### 2. Context Window Optimization via Rolling Buffer
To prevent context window overflow and unbounded token accumulation, I implemented a strict rolling buffer mechanism for the conversation history.
* **Mechanism:** The system tracks the number of user-assistant message pairs. When the history length exceeds the user defined `max_turns` limit (evaluated as `max_turns * 2` messages), the algorithm dynamically truncates the oldest pair using list slicing (`del self.history[0:2]`).
* **Why:** This queue-like approach acts as a sliding window over the conversation. It ensures a constant memory footprint ($O(1)$ space relative to the turn limit) and predictable API costs, preventing API context-length errors and execution bottlenecks as the conversation stretches on. 

### 3. Immutable System Instruction Guardrails
One algorithmic vulnerability of a standard rolling buffer is the potential deletion of the initial system prompt once the turn threshold is breached. To solve this, the `history` array *only* stores the alternating user/assistant turns. When formatting the API request, the `_get_messages_payload()` method dynamically reconstructs the payload array by securely prepending the `system_prompt` at index `0` before attaching the truncated history. This guarantees the model's core behavioral instructions are never lost.

### 4. Interactive Configuration and Graceful Execution
* **Dynamic Sizing:** At runtime, the user is prompted to dynamically define the buffer size (`max_turns`), giving them direct control over the memory-vs-cost tradeoff before execution begins.
* **Model Routing:** A pre-defined dictionary allows the user to easily route requests to different open-source models before the loop begins.
* **Exits:** The conversation loop is wrapped in robust exception handling. It safely catches `/exit` and `/quit` commands, empty string inputs, and `KeyboardInterrupt` (Ctrl+C) signals, ensuring the program terminates cleanly without throwing traceback errors to the terminal.
