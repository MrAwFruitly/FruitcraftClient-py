import pytest
from fruitcraft import FruitCraftClient

@pytest.mark.asyncio
async def test_fruit_client01():
    client = FruitCraftClient()
    load_response = await client.load_player("dear47192650")
    print(load_response.name)

