import os
import sys
from dotenv import load_dotenv

# Ensure the src directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import get_orchestrator

def main():
    load_dotenv()
    
    print("Initializing Oops Red Team Orchestrator...")
    orchestrator = get_orchestrator()
    
    print("Welcome to Oops. Please describe your target and engagement parameters.")
    print("Example: 'I want to perform a red team assessment on my company website, example.com.'")
    
    try:
        user_input = input("\n> ")
        if not user_input:
            print("No input provided. Exiting.")
            return

        print("\n[Oops] Orchestrating agents... Please wait.")
        response = orchestrator.run(user_input)
        
        print("\n[Oops] Operation Complete.")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        print("Check the 'output/' directory for scope.md, intel.md, and plan.md.")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
