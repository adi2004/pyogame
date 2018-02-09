from ogame import OGame
from ogame.constants import Ships, Speed, Missions, Buildings, Research, Defense
from ogame.constants import construct as c

import locale
import time
import random

ogame = None
account = {}
galaxy_infos = []
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
    info = {}
    info.update(ogame.get_planet_infos(p))
    info.update(ogame.get_resources(p))
    info.update(ogame.get_resources_buildings(p))
    info.update(ogame.get_overview(p))
    account[p] = info
    last_id = p


def print_planet(p):
    info = account[p]
    # first part prepare print
    s_planet = "%-8s  " % info["planet_name"]
    s_coord = "[%d:%3d:%3d]: " % (info["coordinate"]["galaxy"], info["coordinate"]["system"], info["coordinate"]["position"])
    s_info = "%3d℃, %2df " % (info["temperature"]["max"], info["fields"]["total"] - info["fields"]["built"])

    # resources formatting
    metal = format_number(info["metal"], info['max_metal'])
    crystal = format_number(info["crystal"], info['max_crystal'])
    deuterium = format_number(info["deuterium"], info['max_deuterium'])

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
    #if len(account[last_id]['research']) > 0:
    #    print("Researching %s" % account[last_id]['research'])

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
        building_satellites = get_satellites_in_queue(info["shipyard"])
        nr_of_ss = needed_satellites - building_satellites
        if nr_of_ss >= 1:
            print("Building on %s %d satellites." % (p, nr_of_ss))
            ogame.build_ships(p, c.solar_satellite, int(nr_of_ss))


def get_satellites_in_queue(arr):
    satellites = 0
    for dictionary in arr:
        if dictionary["name"] == "SolarSatellite":
            satellites += dictionary["quantity"]
    return satellites


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
        if info["metal"] >= info["max_metal"] and ogame.can_build(p, Buildings["metal_storage"], 'supply'):
            print("Building metal_storage %d" % (info["metal_storage"] + 1))
            ogame.build_building(p, Buildings["metal_storage"])
        elif info["crystal"] >= info["max_crystal"] and ogame.can_build(p, Buildings["crystal_storage"], 'supply'):
            print("Building crystal_storage %d" % (info["crystal_storage"] + 1))
            ogame.build_building(p, Buildings["crystal_storage"])
        elif info["deuterium"] >= info["max_deuterium"] and ogame.can_build(p, Buildings["deuterium_tank"], 'supply'):
            print("Building deuterium_tank %d" % (info["deuterium_tank"] + 1))
            ogame.build_building(p, Buildings["deuterium_tank"])


def send_expedition(planet):
    """send expedition with 200 LC"""
    ships = [(c.espionage_probe, 1), (c.large_cargo, 200)]
    speed = Speed['100%']
    galaxy = ogame.get_planet_infos(planet)["coordinate"]["galaxy"]
    system = ogame.get_planet_infos(planet)["coordinate"]["system"]
    where = {'galaxy': galaxy, 'system': system, 'position': 16}
    mission = Missions['Expedition']
    resources = {'metal': 0, 'crystal': 0, 'deuterium': 0}
    print("Sending %d LC to [%d:%d:%d]" % (200, galaxy, system, 16))
    ogame.send_fleet(planet, ships, speed, where, mission, resources)
    time.sleep(2)

def scan_galaxy(galaxy_nr, rng):
    for i in rng:
        print("getting [%d:%3d] " % (galaxy_nr, i))
        galaxy_info = ogame.galaxy_infos(galaxy_nr, i)
        for position_info in galaxy_info:
            if position_info["recyclers_needed"] < 5:
                continue
            g = galaxy_nr
            p = position_info["coordinate"]["position"]
            print("\t[%d:%d:%d] has %d Metal, %d Crystal, %d Recyclers" %
                  ( g, i, p, position_info["metal_debris"], position_info["crystal_debris"],
                    position_info["recyclers_needed"]))

            mine_position = position_info["coordinate"]
            mine_position["recyclers_needed"] = position_info["recyclers_needed"]
            galaxy_infos.append(mine_position)
        time.sleep(0.1)

def mine(planet, number_of_missions):
    mine_info = sorted(galaxy_infos, key=lambda k: k['recyclers_needed'])
    while number_of_missions > 0:
        number_of_missions -= 1
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
            print("Sending %d recyclers to [%d:%d:%d]" % (recycle["recyclers_needed"], galaxy, system, position))
            ogame.send_fleet(planet, ships, speed, where, mission, resources)
            time.sleep(2)

def get_missing_resources(planet, building):
    info = account[planet]
    cost = ogame.calc_building_cost(building, info[building] + 1)
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

def transport(source_planet, destination_planet, resources):
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
    #time.sleep(2)