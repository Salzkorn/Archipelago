from BaseClasses import Item, MultiWorld, Location, Tutorial, ItemClassification, Region, Entrance
from worlds.AutoWorld import WebWorld, World
from .Items import item_name_groups, item_table, Gothic1Item
from .Locations import location_name_groups, location_table
from .Regions import create_regions

class Gothic1WebWorld(WebWorld):
    pass

class Gothic1World(World):
    game = "Gothic 1"
    web = Gothic1WebWorld()
    # option_definitions = 
    item_name_groups = item_name_groups
    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_groups = location_name_groups
    location_name_to_id = {loc.name: loc.code for loc in location_table}

    def create_item(self, name: str) -> Item:
        data = item_table[name]
        return Gothic1Item(name, data.classification, data.code, self.player)

    def create_event(self, event: str):
        return Gothic1Item(event, ItemClassification.progression, None, self.player)

    def create_regions(self):
        self.multiworld.regions += create_regions(self.player, self.multiworld)

    def create_items(self):
        # 50 potions for 50 chests
        pool = [self.create_item("Potion") for _ in range(50)]
        self.multiworld.itempool += pool
    
    def generate_basic(self):
        # place victory check
        self.multiworld.get_location("Sleeper", self.player).place_locked_item(self.create_event("Victory"))
        
    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)