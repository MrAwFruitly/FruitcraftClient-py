import pytest
from fruitcraft import FruitCraftClient

test_token: str = ''

def read_token(file_names: list) -> str:
    global test_token
    for current in file_names:
        try:
            # read the token from token.txt
            test_token = open(current, "r").read()
            return
        except: pass

read_token(['token.txt', '../token.txt', 'tests/token.txt'])

@pytest.mark.asyncio
async def test_fruit_client01():
    client = FruitCraftClient()
    load_response = await client.load_player(test_token)
    print(load_response.name)
    
    
    weakest_card = client.get_weakest_card()
    print(weakest_card.cards)
    
    strongest_cards = client.get_strongest_cards()
    print(strongest_cards)


@pytest.mark.asyncio
async def test_fruit_quest01():
    client = FruitCraftClient()
    load_response = await client.load_player(test_token)
    print(load_response.name)
    
    
    strongest_cards = client.get_strongest_cards()
    print(strongest_cards)
    
    quest_result = await client.do_quest(strongest_cards)
    print(quest_result.xp_added)
