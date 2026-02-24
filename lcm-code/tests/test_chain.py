import asyncio
from lcm import AI

async def main():
    ai = AI(verbose=True)
    
    print("🚀 Testing Catchy Chaining...")
    
    # pipe -> then -> jsononly 🧱
    result = await ai.pipe("The first moon landing was in 1969 by Apollo 11.") \
               .then("Extract the year and the mission name as JSON") \
               .jsononly
               
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())
