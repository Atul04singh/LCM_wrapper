import asyncio
from lcm import AI

async def main():
    ai = AI(verbose=True)
    
    print("🛠️ Testing Middleware...")
    
    # Define a simple middleware that adds a system prompt
    @ai.use
    def custom_persona(messages):
        print("--- Middleware Triggered! ---")
        messages.insert(0, {"role": "system", "content": "You are a helpful pirate."})
        return messages
    
    res = await ai.ask("Hello, who are you?")
    print(f"\nAI: {res}")

if __name__ == "__main__":
    asyncio.run(main())
