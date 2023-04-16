#####################
# The YAML files included here are dumped by the game and should not be edited.
# The order of elements in these files is not stable across dumps.
# Their structure is documented below.
#####################
# npcs.yaml
#####################
# - id: 217
#   obj: "GRD_217_TORWACHE"
#   name: "Torwache"
#   weapon:
#   - obj: "ITMW_1H_SWORD_01"
#     name: "grobes Schwert"
#     amount: 1
#   - ...
#   armor: ...
#   rune: ...
#   magic: ...
#   food: ...
#   potion: ...
#   doc: ...
#   misc: ...
# - ...
#
#####################
# containers.yaml
#####################
# - obj: "CHEST"
#   name: "Chest"
#   contents:
#   - obj: "ITMINUGGET"
#     name: "Erzbrocken"
#     amount: 25
#   - ...
# - ...
#
#####################
# items.yaml
#####################
# - obj: "ITMNUGGET"
#   name: "Erzbrocken"
#   amount: 1
# - ...
#
#####################
# objects.yaml
#####################
# - "CHAIR_1"
# - ...
#
#####################

import yaml
from os import path
with open(path.join(path.dirname(__file__), "npcs.yaml")) as file:
    npcs = yaml.safe_load(file)
with open(path.join(path.dirname(__file__), "containers.yaml")) as file:
    containers = yaml.safe_load(file)
with open(path.join(path.dirname(__file__), "items.yaml")) as file:
    items = yaml.safe_load(file)