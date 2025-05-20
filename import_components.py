from src.DB.Component import Component
import asyncio
import json

async def import_components():
    try:
        with open("components.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("components.json file not found.")
        return

    for item in data:
        # Check if a component with the same name already exists
        existing = await Component.find_one({"name": item.get("name")})
        if existing:
            print(f"Component with name '{item.get('name')}' already exists. Skipping insert.")
            continue
        component = Component(**item)
        await component.save()

    print(f"Imported components from components.json")

if __name__ == "__main__":
    asyncio.run(import_components())
