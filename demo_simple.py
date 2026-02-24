from lcm import AI

def main():
    # Using the new catchy 'AI' class
    ai = AI(verbose=True)
    
    print("--- SYNC ASK ---")
    response = ai.ask_sync("What is 2+2?")
    print(f"AI: {response}")
    
    print("\n--- SYNC FLOW ---")
    # Using 'flow_sync' for character-by-character typing
    for token in ai.flow_sync("Count to 5 slowly."):
        print(token, end="", flush=True)
    
    print("\n\nDone. 🚀")

if __name__ == "__main__":
    main()
