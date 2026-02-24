import asyncio
from lcm import AI

async def main():
    ai = AI(verbose=True)
    
    print("🧠 Testing Memory (remember/forget)...")
    
    ai.remember()
    print("\nStep 1: Telling AI my name...")
    await ai.ask("My name is Antigravity.")
    
    print("\nStep 2: Asking AI what my name is...")
    res = await ai.ask("Do you remember my name?")
    print(f"AI: {res}")
    
    ai.forget()
    print("\nStep 3: After .forget(), asking again...")
    res2 = await ai.ask("Do you remember my name?")
    print(f"AI: {res2}")

if __name__ == "__main__":
    asyncio.run(main())
