from ogame import OGame
from ogame.constants import Ships, Speed, Missions, Buildings, Research, Defense
from ogame.constants import construct as c

import locale
import time
import random
import json

print("Loading helpers.py...")

if 'ogame' not in locals():
    print("resetting ogame var")
    ogame = None
account = {}

last_id = '33667257'
gen = {}

class col:
    RED = '\033[91m'
    ORANGE = '\033[93m'
    GREEN = '\033[92m'
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


def test_stuff():
    st = ogame.calc_storage_size(7)
    print(st)


def read_planet(p):
    global last_id
    info = {}
    info.update(ogame.get_planet_infos(p))
    info.update(ogame.get_resources(p))
    info.update(ogame.get_resources_buildings(p))
    info.update(ogame.get_overview(p))
    if p in account:
        account[p].update(info)
    else:
        account[p] = info
    last_id = p

def read_planet_defense(planet):
    d = ogame.get_defense(planet)
    account[planet]["defense"] = d

def read_file(file_name):
    f = open(file_name, "r")
    f_str = f.read()
    account.update(json.loads(f_str))
    f.close()

def print_planet(p):
    info = account[p]
    # first part prepare print
    s_planet = "%-15s  " % info["planet_name"]
    s_coord = "[%d:%3d:%3d]: " % (info["coordinate"]["galaxy"], info["coordinate"]["system"], info["coordinate"]["position"])
    s_info = "%3d℃, %2df " % (info["temperature"]["max"], info["fields"]["total"] - info["fields"]["built"])

    # resources formatting
    metal = format_number(info["metal"], info['metal_max'])
    crystal = format_number(info["crystal"], info['crystal_max'])
    deuterium = format_number(info["deuterium"], info['deuterium_max'])

    e = info["energy"]
    energy = "%d" % e
    if e < 0:
        energy = col.RED + energy + col.ENDC
    else:
        energy = col.GREEN + energy + col.ENDC

    s_res = "m: %19s, c: %19s, d: %19s, e: %14s" % (metal, crystal, deuterium, energy)

    # first part print
    print(s_planet + s_coord + s_info + s_res)

    # second part print
    status_string = ""
    if len(info["buildings"]) > 0:
        status_string = "\tBuilding: " + info["buildings"][0]["name"]
    if len(info["shipyard"]) > 0:
        status_string += "\tShipyard: "
    for ships in info["shipyard"]:
        status_string += str(ships["quantity"]) + "x" + ships["name"] + " "
    if len(status_string):
        print(status_string)


def print_account():
    # print("General info")
    gen.update(ogame.general_get_user_infos())
    print("%s, rank %d, points %d, honour_points %d, planets %s/%s" %
          (gen["player_name"], gen["rank"], gen["points"], gen["honour_points"],
           gen["current_planets"], gen["max_planets"]))
    if len(account[last_id]['research']) > 0:
       print("Researching %s" % account[last_id]['research'])

    gen.update(ogame.get_flying_fleets())
    print("Fleets %d / %d" % (gen["current_fleets"], gen["max_fleets"]))

    msg = ogame.get_new_messages()
    if len(msg) > 0:
        print("You have messages %s" % msg)


def format_number(number, max_capacity):
    current = locale.getlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, 'ro_RO.UTF-8')
    number_string = locale.format('%d', number, True)
    locale.setlocale(locale.LC_ALL, current)
    if number/max_capacity < 0.9:
        return col.GREEN + number_string + col.ENDC
    if number/max_capacity < 1:
        return col.ORANGE + number_string + col.ENDC
    return col.RED + number_string + col.ENDC


def fix_energy(p):
    info = account[p]
    energy = info["energy"]
    if energy < 0:
        needed_satellites = 1 + -energy / 40
        building_satellites = get_shipyard_queue_item(p, c.solar_satellite)
        nr_of_ss = needed_satellites - building_satellites
        if nr_of_ss >= 1:
            print("Building on %s %d satellites." % (p, nr_of_ss))
            ogame.build_ships(p, c.solar_satellite, int(nr_of_ss))

def fix_defense(p):
    current = account[p]["defense"]
    target = account[p]["defenses_levels"]
    for dkey, dcount in current.items():
        if target[dkey] < dcount:
            continue

        dmissing = target[dkey] - dcount - get_shipyard_queue_item(p, Defense[dkey])

        if dmissing > 0:
            print("Building %s x%d" % (dkey, dmissing))
            ogame.build_defense(p, Defense[dkey], dmissing)

def get_shipyard_queue_item(p, id):
    queue = account[p]["shipyard"]
    item_count = 0
    for dictionary in queue:
        if dictionary["code"] == id:
            item_count += dictionary["quantity"]
    return item_count


def build_resources(p):
    info = account[p]
    if not info["isUnderConstruction"]:
        mines = {}
        mines["metal_mine"] = info["metal_mine"]
        mines["crystal_mine"] = info["crystal_mine"]
        mines["deuterium_synthesizer"] = info["deuterium_synthesizer"]
        for m in sorted(mines, key=mines.get):
            if ogame.can_build(p, Buildings[m], 'supply'):
                print("Building %s %d" % (m, mines[m] + 1))
                ogame.build_building(p, Buildings[m])
                return


def build_storage(p):
    info = account[p]
    if not info["isUnderConstruction"]:
        if info["metal"] >= info["metal_max"] and ogame.can_build(p, Buildings["metal_storage"], 'supply'):
            print("Building metal_storage %d" % (info["metal_storage"] + 1))
            ogame.build_building(p, Buildings["metal_storage"])
        elif info["crystal"] >= info["crystal_max"] and ogame.can_build(p, Buildings["crystal_storage"], 'supply'):
            print("Building crystal_storage %d" % (info["crystal_storage"] + 1))
            ogame.build_building(p, Buildings["crystal_storage"])
        elif info["deuterium"] >= info["deuterium_max"] and ogame.can_build(p, Buildings["deuterium_tank"], 'supply'):
            print("Building deuterium_tank %d" % (info["deuterium_tank"] + 1))
            ogame.build_building(p, Buildings["deuterium_tank"])


def send_expedition(planet, large_cargo_count = 200):
    """send expedition with 200 LC"""
    ships = [(c.espionage_probe, 1), (c.large_cargo, large_cargo_count)]
    speed = Speed['100%']
    galaxy = ogame.get_planet_infos(planet)["coordinate"]["galaxy"]
    system = ogame.get_planet_infos(planet)["coordinate"]["system"]
    where = {'galaxy': galaxy, 'system': system, 'position': 16}
    mission = Missions['Expedition']
    resources = {'metal': 0, 'crystal': 0, 'deuterium': 0}
    if "available_fleets" not in gen:
        gen.update(ogame.get_flying_fleets())
    if gen["available_fleets"] > 0:
        print("Sending %d LC to [%d:%d:%d]" % (large_cargo_count, galaxy, system, 16))
        ogame.send_fleet(planet, ships, speed, where, mission, resources)
    else:
        return False


def scan_galaxy_infos(galaxy_range, systems_range):
    gi = []
    for g in galaxy_range:
        for s in systems_range:
            print("getting [%d:%3d] " % (g, s))
            galaxy_info = ogame.galaxy_infos(g, s)
            for position_info in galaxy_info:
                if position_info["recyclers_needed"] < 5:
                    continue
                p = position_info["coordinate"]["position"]
                print("\t[%d:%d:%d] has %d Metal, %d Crystal, %d Recyclers" %
                      ( g, s, p, position_info["metal_debris"], position_info["crystal_debris"],
                        position_info["recyclers_needed"]))

                mine_position = position_info["coordinate"]
                mine_position["recyclers_needed"] = position_info["recyclers_needed"]
                gi.append(mine_position)
            time.sleep(0.1)
    return gi

def mine(planet, galaxy_infos, max_missions):
    mine_info = sorted(galaxy_infos, key=lambda k: k['recyclers_needed'])
    while max_missions > 0:
        max_missions -= 1
        if len(mine_info) > 0:
            recycle = mine_info.pop()
            ships = [(c.recycler, recycle["recyclers_needed"])]
            speed = Speed['100%']
            galaxy = recycle["galaxy"]
            system = recycle["system"]
            position = recycle["position"]
            where = {'galaxy': galaxy, 'system': system, 'position': position, 'type': 2}
            mission = Missions['RecycleDebrisField']
            resources = {'metal': 0, 'crystal': 0, 'deuterium': 0}
            recyclers = 100 if recycle["recyclers_needed"] > 100 else recycle["recyclers_needed"]
            print("Sending %d recyclers to [%d:%d:%d]" % (recyclers, galaxy, system, position))
            ogame.send_fleet(planet, ships, speed, where, mission, resources)

def get_resources(planet, building_str = "", level_diff = 1):
    info = account[planet]
    cost = {}
    if building_str == "":
        cost['metal'] = 0
        cost['crystal'] = 0
        cost['deuterium'] = 0
    else:
        cost = ogame.calc_building_cost(building_str, info[building_str] + level_diff)
    missing = {}
    missing['metal'] = cost['metal'] - info['metal']
    if missing['metal'] < 0:
        missing['metal'] = 0
    missing['crystal'] = cost['crystal'] - info['crystal']
    if missing['crystal'] < 0:
        missing['crystal'] = 0
    missing['deuterium'] = cost['deuterium'] - info['deuterium']
    if missing['deuterium'] < 0:
        missing['deuterium'] = 0

    return missing

def transport(source_planet, destination_planet, resources = {}):
    if resources == {} and account[source_planet]["metal"] != {}:
        resources["metal"] = account[source_planet]["metal"]
        resources["crystal"] = account[source_planet]["crystal"]
        resources["deuterium"] = account[source_planet]["deuterium"]
    larce_cargoes_needed = 1 + int((resources['metal'] + resources['crystal'] + resources['deuterium']) / 25000)
    ships = [(c.large_cargo, larce_cargoes_needed)]
    speed = Speed['100%']
    destination_coords = account[destination_planet]["coordinate"]
    galaxy = destination_coords["galaxy"]
    system = destination_coords["system"]
    position = destination_coords["position"]
    where = {'galaxy': galaxy, 'system': system, 'position': position, 'type': 1}
    mission = Missions['Transport']
    resources = {
        'metal': resources['metal'],
        'crystal': resources['crystal'],
        'deuterium': resources['deuterium']
    }
    print("Sending %d cargoes to [%d:%d:%d]" % (larce_cargoes_needed, galaxy, system, position))
    ogame.send_fleet(source_planet, ships, speed, where, mission, resources)
