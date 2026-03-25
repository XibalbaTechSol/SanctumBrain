import os
import sys

# Ensure we can import from the hermes directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "hermes"))

from run_agent import AIAgent
from hermes_cli.config import load_config

def main():
    print("🧠 SanctumBrain Initializing...")
    print("Integrating Hermes with The Agency specialists...")
    
    # Load default config
    config = load_config()
    
    # Ensure agency toolset is enabled
    enabled_toolsets = config.get("enabled_toolsets", [])
    if "agency" not in enabled_toolsets:
        enabled_toolsets.append("agency")
    
    # Initialize the main agent
    # Note: In a real scenario, we'd want to use a model that supports tool calling.
    # We'll use the default from config.
    model = config.get("model", "anthropic/claude-3-5-sonnet-20241022")
    
    # Define the handful of specialists Hermes should prioritize
    SPECIALISTS = [
        "engineering-senior-developer",
        "product-manager",
        "marketing-growth-hacker",
        "testing-quality-assurance-specialist",
        "design-visual-designer"
    ]
    
    # Custom system prompt part
    specialist_guidance = f"\n\nYou are SanctumBrain, an advanced AI orchestrator. " \
                          f"You have direct access to a team of Agency specialists. " \
                          f"When a task requires deep expertise in a specific domain, " \
                          f"use the 'delegate_specialist' tool to invoke one of these specialists:\n" \
                          f"- " + "\n- ".join(SPECIALISTS) + "\n" \
                          f"Use 'list_specialists' to see all other available experts."

    agent = AIAgent(
        model=model,
        enabled_toolsets=enabled_toolsets,
        platform="cli",
        ephemeral_system_prompt=specialist_guidance # This will be appended to the base prompt
    )
    
    print(f"SanctumBrain is ready (using {model}).")
    print("You can now delegate tasks to Agency specialists using 'delegate_specialist'.")
    print("Type '/help' for more commands or start chatting!")
    
    # Since this is a simple project, we'll just hand over to the Hermes CLI or run a simple loop.
    # But to follow the "handful of specialists" requirement, we'll pre-prime it in the system prompt.
    
    # Actually, Hermes CLI handles the interaction well.
    # For this project, we'll just run a simple chat interface for now.
    
    try:
        while True:
            user_input = input("\n👤 You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            response = agent.run_conversation(user_input)
            print(f"\n🧠 SanctumBrain: {response['final_response']}")
    except KeyboardInterrupt:
        print("\nSanctumBrain shutting down.")

if __name__ == "__main__":
    main()
