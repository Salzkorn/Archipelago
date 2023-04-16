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

item_table = {
    "Potion": ItemData(0 + GOTHIC_ITEM_OFFSET, "ItFo_Potion_Health_01", "Potions"),
}

item_name_groups = {}
for item, data in item_table.items():
    item_name_groups.setdefault(data.type, []).append(item)

item_id_to_name = {item.code: name for name, item in item_table.items() if item.code}