from BaseClasses import Location, MultiWorld
from typing import NamedTuple, Callable
# from .dumps import npcs

GOTHIC_LOCATION_OFFSET = 5353500

class Gothic1Location(Location):
    game: str = "Gothic 1"

    def __init__(self, player: int, name = "", code = None, parent = None):
        super(Gothic1Location, self).__init__(player, name, code, parent)
        self.event = code is None

class LocationData(NamedTuple):
    type: str
    name: str
    code: int
    rule: Callable = lambda state: True

CHEST_MAX_AMOUNT = 50

_chest_locations = [LocationData("Chests", f"Chest {code + 1}", code + GOTHIC_LOCATION_OFFSET) for code in range(CHEST_MAX_AMOUNT)]

# Filter unique NPCs
_npc_locations = []
# _npc_cache = {}
# _npc_code = CHEST_MAX_AMOUNT
# for npc in npcs:
#     _npc_cache.setdefault(npc['id'], []).append(npc['name'])
# for id in _npc_cache:
#     if len(_npc_cache[id]) == 1:
#         _npc_locations.append(LocationData("NPCs", _npc_cache[id][0], _npc_code))
#         _npc_code += 1

location_table = tuple(_chest_locations + _npc_locations)

location_name_groups = {}
for loc in location_table:
    location_name_groups.setdefault(loc.type, []).append(loc.name)