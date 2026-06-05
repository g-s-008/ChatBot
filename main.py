import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ChatAgent:
    """
    A model-agnostic ChatAgent that interfaces with OpenRouter.
    Manages a rolling buffer conversation history.
    """
    def __init__(self, model: str, max_turns: int = 5, system_prompt: str = "You are a helpful assistant."):
        # Configuration options
        self.model = model
        self.max_turns = max_turns
        self.system_prompt = system_prompt
        
        # Load API key from environment
        self.api_key = os.getenv("OPENROUTER_API_KEY")
            
        # Initialize OpenAI client pointing to OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
        # Initialize conversation history (stores only user/assistant pairs)
        self.history = []

    def _get_messages_payload(self) -> list:
        """Constructs the full message list including the system prompt."""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        return messages

    def call_model(self, user_input: str):
        """
        Main method to interact with the model. Handles buffer limits,
        appends user messages, calls the API, and stores the response.
        """
        # Append the new user message
        self.history.append({"role": "user", "content": user_input})
        
        # Check buffer overflow (1 turn = 1 user message + 1 assistant message)
        # So max_messages = max_turns * 2
        # If we exceed it, drop the oldest user-assistant pair (index 0 and 1)
        if len(self.history) > (self.max_turns * 2):
            del self.history[0:2]
        
        #API Call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._get_messages_payload(),
            stream=False
        )

        # Extract and print response
        assistant_response = response.choices[0].message.content
        print(assistant_response)

        # Append the model's response to history
        self.history.append({"role": "assistant", "content": assistant_response})


def main():
    print("=== Welcome to the OpenRouter ChatAgent ===")
    
    # 1. Model Selection
    models = {
        "1": "openrouter/free",
        "2": "mistralai/mistral-7b-instruct:free",
        "3": "google/gemma-7b-it:free"
    }
    
    print("Available Models:")
    for key, model_name in models.items():
        print(f"[{key}] {model_name}")
        
    choice = input("Select a model (1-3) [Default: 1]: ").strip()
    selected_model = models.get(choice, models["1"])
    
    n=int(input("Choose your rolling buffer size: "))
    agent = ChatAgent(
        model=selected_model,
        max_turns=n
    )
    
    print(f"\n[System: Chat started with {selected_model}. Type '/exit' to quit.]\n")

    # 3. Multi-turn conversation loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            # Handle exit command
            if user_input.lower() in ['/exit', '/quit']:
                print("Goodbye!")
                break
                
            # Chat with model
            print("Assistant: ", end="", flush=True)
            agent.call_model(user_input)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()