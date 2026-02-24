import asyncio
from lcm import AI

async def main():
    ai = AI(verbose=True)
    
    print("💎 Testing Data Extraction...")
    
    schema = {
        "name": "string",
        "role": "string",
        "experience_years": "number"
    }
    
    data = await ai.extract(
        "I am Sarah, a Senior Architect with 12 years in the cloud industry my friend name is atul .",
        schema=schema
    )
    
    print(f"\nExtracted Data: {data}")

if __name__ == "__main__":
    asyncio.run(main())
