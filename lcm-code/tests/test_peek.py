import asyncio
from lcm import AI

async def main():
    ai = AI(verbose=True)
    
    print("👀 Testing AI Peek (Health Check)...")
    await ai.peek()

if __name__ == "__main__":
    asyncio.run(main())
