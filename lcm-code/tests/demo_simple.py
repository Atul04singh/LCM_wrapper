from lcm import Model

def main():
    # No asyncio, no async/await!
    model = Model()
    
    print("--- SYNC CHAT ---")
    response = model.chat_sync("What is 2+2?")
    print(f"AI: {response}")
    
    print("\n--- SYNC STREAM ---")
    # Using a simple for-loop
    for token in model.stream_sync("Count to 5 slowly."):
        print(token, end="", flush=True)
    
    print("\n\nDone.")

if __name__ == "__main__":
    main()
