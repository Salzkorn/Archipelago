from BaseClasses import Item, ItemClassification, MultiWorld
import typing

class ItemData(typing.NamedTuple):
    code: int
    inst: str # instance name from the item definition in the game files
    type: str
    classification: ItemClassification = ItemClassification.useful

class Gothic1Item(Item):
    game: str = "Gothic 1"

GOTHIC_ITEM_OFFSET = 5353500

# selection of reasonably useful items
item_table = {
    "Health Elixir": ItemData(0 + GOTHIC_ITEM_OFFSET, "ItFo_Potion_Health_03", "Potions"),
    "Strength Elixir": ItemData(1 + GOTHIC_ITEM_OFFSET, "ItFo_Potion_Strength_03", "Potions"),
    "Dexterity Elixir": ItemData(2 + GOTHIC_ITEM_OFFSET, "ItFo_Potion_Dex_03", "Potions"),
    "Life Elixir": ItemData(3 + GOTHIC_ITEM_OFFSET, "ItFo_Potion_Health_Perma_03", "Potions"),
    "Mana Elixir": ItemData(4 + GOTHIC_ITEM_OFFSET, "ItFo_Potion_Mana_Perma_03", "Potions"),
    "Haste Elixir": ItemData(5 + GOTHIC_ITEM_OFFSET, "ItFo_Potion_Haste_03", "Potions"),
    "Amulet of Might": ItemData(6 + GOTHIC_ITEM_OFFSET, "Amulett_der_Macht", "Potions"),
    "Amulet of Life": ItemData(7 + GOTHIC_ITEM_OFFSET, "Lebensamulett", "Potions"),
    "Ring of Invincibility": ItemData(8 + GOTHIC_ITEM_OFFSET, "Schutzring_Total2", "Potions"),
    "Ring of Enlightenment": ItemData(9 + GOTHIC_ITEM_OFFSET, "Ring_der_Erleuchtung", "Potions"),
    "Ring of Might": ItemData(10 + GOTHIC_ITEM_OFFSET, "Machtring", "Potions"),
    "Ore": ItemData(11 + GOTHIC_ITEM_OFFSET, "ItMiNugget", "Potions"),
    "Torch": ItemData(12 + GOTHIC_ITEM_OFFSET, "ItLsTorch", "Potions"),
}

item_name_groups = {}
for item, data in item_table.items():
    item_name_groups.setdefault(data.type, []).append(item)

item_id_to_name = {item.code: name for name, item in item_table.items() if item.code}