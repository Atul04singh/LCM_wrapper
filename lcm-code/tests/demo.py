import asyncio
from lcm import Model

async def main():
    model = Model()
    
    print("AI is thinking...", flush=True)
    
    async for token in model.stream("Tell me a short story about a brave cat."):
        print(token, end="", flush=True)
    
    print("\n\nDone.")

if __name__ == "__main__":
    asyncio.run(main())