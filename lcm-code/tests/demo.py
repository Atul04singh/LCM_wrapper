import asyncio
from lcm import AI

async def main():
    # 'AI' replaces 'Model' 🚀
    ai = AI(verbose=True) 
    
    # 'flow' replaces 'stream' 🌊
    async for token in ai.flow("Tell me a short story about a brave cat."):
        print(token, end="", flush=True)
    
    print("\n\nDone. 🚀")

if __name__ == "__main__":
    asyncio.run(main())