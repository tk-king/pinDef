from src.DB.Component import Component
import json


async def export_components():
    components = await Component.find().to_list()

    # Delete the flag from the components
    for component in components:
        if hasattr(component, "flag"):
            del component.flag
        if hasattr(component, "id"):
            del component.id
        
    
    # Save the components to a json file as a JSON array
    with open("components.json", "w") as f:
        json_list = [json.loads(component.json()) for component in components]
        json.dump(json_list, f, indent=4)
    print(f"Exported {len(components)} components to components.json")



if __name__ == "__main__":
    import asyncio
    asyncio.run(export_components())
