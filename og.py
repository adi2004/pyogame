from ogame import OGame
from pprint import pprint as pp
import PrintColor
import json
from helpers import *
from ogame import constants
import random

pc = PrintColor.PrintColor
pp.red = pc.red

class Account:
    """The bot contains an instance to the main page of the app"""

    # ogame logic
    ogame = None

    # data dictionary
    data = {}

    # array of planets and moons
    planets = []

    # persistance file
    file = "ogame.json"

    def __init__(self):
        print("Account.__init__")

    def login(self, universe, user, password, cookiePath = ""):
        pc.yellow("Logging in with %s" % user, end = " ")

        try:
            self.ogame = OGame(universe, user, password)
        except Exception as e:
           pp.red("Failed to login %s. Exception: " % user + str(e))
        else:
            if self.ogame.is_logged():
                pc.green("Success!")
                for p in self.planets:
                    p.ogame = self.ogame

    #
    # Fetching functions (they display only status messages, not the data fetched)
    #

    def fetch_general(self):
        pc.yellow("Updating general user info")
        self.ogame.general_get_user_infos()

    def fetch_planets(self):
        if self.ogame is None:
            pp.red("Not logged in")
            return

        # read from the server
        pc.yellow("Updating all planet ids...")
        planets = self.ogame.get_planet_ids() + self.ogame.get_moon_ids()

        # convert to dict and save in data
        planets_dict = {}
        for p in planets:
            pc.yellow("Reading " + p, end = "")
            planet_overview = self.ogame.get_planet_infos(p)
            planets_dict[planet_overview["planet_name"]] = planet_overview
            pc.green(" OK for " + planet_overview["planet_name"])

        # update the class member
        if "planets" not in self.data:
            self.data["planets"] = {}

        self.data["planets"].update(planets_dict)

    def fetch_account(self):
        #TODO: implement this
        if self.ogame is None:
            pp.red("Not logged in")
            return

    #
    # Print general account informations (rank, name, research queue, messages)
    #

    def pp(self):
        for planet in self.planets:
            planet.pp()

    #
    # Persistance functions
    #

    def load(self, file_name = None):
        """Reads the data from a json file"""
        if file_name is not None and self.file != file_name:
            print("Setting file to %s" % file_name)
            self.file = file_name
        file_name = self.file
        pc.bold("Loading %s" % file_name, end = " ")
        try:
            f = open(file_name, "r")
            data = f.read()
            f.close()
            # data = '{"planet": {"mines": "none"}, "moon": {"produciton": "tbd"}}'
            self.data = json.loads(data)
        except Exception as e:
            pp.red("JSON format error: " + str(e))
        else:
            self.init_planets()
            pc.green("Done.")

    def save(self, file_name = None):
        if file_name is not None and self.file != file_name:
            pp("Setting file to %s", file_name)
        file_name = self.file
        pc.bold("Saving to %s" % file_name, end = " ")

        # updated data
        for p in self.planets:
            if p.name() not in self.data["planets"]:
                self.data["planets"][p.name()] = {}
            self.data["planets"][p.name()].update(p.data)

        # write to file
        try:
            f = open(file_name, "w")
            f.write(json.dumps(self.data, indent=4))
            f.close()
        except Exception as e:
            pp.red("Something went wrong: " + str(e))
        else:
            pc.green("Done.")

    #
    # Data manipulation
    #

    def planet_data(self, planet_id):
        """Given an ID returns the planet data source (aka data)"""
        for planet in self.planets:
            if planet.id() == planet_id:
                return planet.data

    def init_planets(self):
        """Given an existing data, gets the `planets` key and creates attributes on the `Account` class"""
        if 'planets' not in self.data:
            pc.red("Unable to initialize `planets`. No `planets` key found in `self.data`")
        self.planets = []
        for k, v in self.data['planets'].items():
            planet = Planet(self, v)
            self.planets.append(planet)
            self.__setattr__(k.lower(), planet)

class Planet:
    data = {}
    acc = None
    ogame = None

    def __init__(self, acc, data):
        self.data = data
        self.acc = acc
        self.ogame = acc.ogame

    def id(self):
        return self.data['id']

    def name(self):
        return self.data['planet_name']

    def merge(self, new_data):
        merge_dict(self.data, new_data)

    def pp_name(self):
        #TODO: not used, remove
        pp("%5s" % self.name())

    #
    # Fetching functions (reads remote account)
    #

    def fetch_infos(self):
        pc.yellow("Reading %s infos... " % self.name(), end = " ")
        self.data.update(self.ogame.get_planet_infos(self.id()))
        pc.green("Done!")

    def fetch_resources(self):
        pc.yellow("Reading %s resources... " % self.name(), end=" ")
        info = dict()
        info["resources"] = self.ogame.get_resources(self.id())
        self.data.update(info)
        pc.green("Done!")


    def fetch_buildings(self):
        pc.yellow("Reading %s buildings... " % self.name(), end=" ")
        info = dict()
        info["buildings"] = self.ogame.get_resources_buildings(self.id())
        self.data.update(info)
        pc.green("Done!")

    def fetch_facilities(self):
        pc.yellow("Reading %s facilities... " % self.name(), end=" ")
        info = dict()
        info["facilities"] = self.ogame.get_facilities(self.id())
        self.data.update(info)
        pc.green("Done!")

    def fetch_ships(self):
        pc.yellow("Reading %s ships... " % self.name(), end=" ")
        info = dict()
        info["ships"] = self.ogame.get_ships(self.id())
        self.data.update(info)
        pc.green("Done!")

    def fetch_defense(self):
        pc.yellow("Reading %s defense... " % self.name(), end=" ")
        self.data["defense"] = self.ogame.get_defense(self.id())
        pc.green("Done!")

    def fetch_queue(self):
        pc.yellow("Reading %s queue... " % self.name(), end = " ")
        info = dict()
        info["queue"] = self.ogame.get_overview(self.id())
        self.data.update(info)
        pc.green("Done!")

    def fetch_fleet(self):
        pass

    def fetch(self):
        self.fetch_infos()
        self.fetch_resources()
        self.fetch_buildings()
        self.fetch_facilities()
        self.fetch_ships()
        self.fetch_queue()
        self.fetch_defense()
        self.fetch_fleet()

    #
    # Printing functions (only displays data that was read before)
    #

    def _pp(self, string):
        if "planet_name" not in self.data:
            pc.red("data not fetched.")
            return
        print("%-15s  " % self.data["planet_name"] + string)

    def _pp_items(self, items):
        print_string = ""
        for key, value in items:
            if value > 0:
                print_string += "%s %d; " % (constants.get_constant(key).short, value)
        self._pp(print_string)

    def pp_info(self):
        if "planet_name" not in self.data:
            pc.red("Resources data not fetched.")
            return

        info = self.data

        s_coord = "%-8s  " % info["coordinate"]["as_string"]
        s_temp = info["temperature"]["max"] if "max" in info["temperature"] else 0
        s_info = "%3d℃, %2df " % (s_temp, info["fields"]["total"] - info["fields"]["built"])

        self._pp(s_coord + s_info)

    def pp_resources(self):
        if "resources" not in self.data:
            pc.red("Resources data not fetched.")
            return

        info = self.data

        # resources formatting
        res = info["resources"]
        metal = format_number(res["metal"], res['metal_max'])
        crystal = format_number(res["crystal"], res['crystal_max'])
        deuterium = format_number(res["deuterium"], res['deuterium_max'])
        energy = format_number(res["energy"])

        s_res = "m: %19s, c: %19s, d: %19s, e: %14s" % (metal, crystal, deuterium, energy)

        self._pp(s_res)

    def pp_building_queue(self):
        if "queue" not in self.data:
            pc.red("Planet data not fetched.")
            return

        info = self.data["queue"]

        if len(info["buildings"]) > 0:
            status_string = "Building: " + info["buildings"][0]["name"]
            self._pp(status_string)
        else:
            self._pp("Building queue is empty")

    def pp_shipyard_queue(self):
        if "queue" not in self.data:
            pc.red("Planet data not fetched.")
            return

        info = self.data["queue"]

        status_string = ""
        if len(info["shipyard"]) > 0:
            status_string += "Shipyard: "
        for ships in info["shipyard"]:
            status_string += str(ships["quantity"]) + "x" + ships["name"] + " "

        if len(status_string):
            self._pp(status_string)
        else:
            self._pp("Shipyard queue is empty")

    def pp_buildings(self):
        self._pp_items(self.data["buildings"].items())

    def pp_facilities(self):
        self._pp_items(self.data["facilities"].items())

    def pp_ships(self):
        self._pp_items(self.data["ships"].items())

    def pp_defense(self):
        self._pp_items(self.data["defense"].items())

    def pp_fleet(self):
        pass

    def pp(self):
        self.pp_info()
        self.pp_resources()
        self.pp_buildings()
        self.pp_facilities()
        self.pp_ships()
        self.pp_defense()
        self.pp_building_queue()
        self.pp_shipyard_queue()
        self.pp_fleet()

    #
    # Actions (build stuff, transport)
    #

    def fix_energy(self):
        p = self.id()
        energy = self.data["resources"]["energy"]

        if energy < 0:
            needed_satellites = 1 + -energy / 40
            building_satellites = self._shipyard_queue(c.solar_satellite)
            nr_of_ss = needed_satellites - building_satellites
            if nr_of_ss >= 1:
                print("Building on %s %d satellites." % (p, nr_of_ss))
                self.ogame.build_ships(p, c.solar_satellite, int(nr_of_ss))

    def fix_defense(self):
        if "defense_fix" not in self.data:
            pc.red("No `defense_fix` key created for " + self.name())
            return

        current = self.data["defense"]
        target = self.data["defense_fix"]

        for dkey, dcount in current.items():
            if dkey not in target:
                continue
            if target[dkey] < dcount:
                continue

            dmissing = target[dkey] - dcount - self._shipyard_queue(Defense[dkey])

            if dmissing > 0 and self.ogame.can_build_defenses(self.id(), dkey):
                print("Building %s x%d" % (dkey, dmissing))
                self.ogame.build_defense(self.id(), Defense[dkey], dmissing)

    def _shipyard_queue(self, item_id):
        queue = self.data["queue"]["shipyard"]
        item_count = 0
        for dictionary in queue:
            if dictionary["code"] == item_id:
                item_count += dictionary["quantity"]
        return item_count

    def get_resources(self, building_str="", level_diff=1):
        """Calculates the resources needed to build new building higher with level_diff then the current level"""
        res = self.data["resources"]

        cost = {}
        if building_str == "":
            cost['metal'] = 0
            cost['crystal'] = 0
            cost['deuterium'] = 0
        else:
            building_lvl = self.data["buildings"][building_str] + level_diff
            cost = OGame.calc_building_cost(building_str, building_lvl)

        missing = dict()
        missing['metal'] = max(0, cost['metal'] - res['metal'])
        missing['crystal'] = max(0, cost['crystal'] - res['crystal'])
        missing['deuterium'] = max(0, cost['deuterium'] - res['deuterium'])

        return missing

    def scan_galaxy_infos(self, galaxy_range, systems_range, min_recyclers = 5):
        gi = []
        for g in galaxy_range:
            print("Scanning galaxy %d:" % g)
            for s in systems_range:
                print("%d " % s, end="", flush=True)
                galaxy_info = self.ogame.galaxy_infos(g, s)
                for position_info in galaxy_info:
                    if position_info["recyclers_needed"] < min_recyclers:
                        continue
                    p = position_info["coordinate"]["position"]
                    print("[%d:%d:%d] has %d Metal, %d Crystal, %d Recyclers" %
                          (g, s, p, position_info["metal_debris"], position_info["crystal_debris"],
                           position_info["recyclers_needed"]))

                    mine_position = position_info["coordinate"]
                    mine_position["recyclers_needed"] = position_info["recyclers_needed"]
                    gi.append(mine_position)
                # time.sleep(0.1)
            print("Done!")
        return gi

    def mine(self, galaxy_infos, max_missions = 5, min_recyclers = 5, max_recyclers = 100):
        mine_info = sorted(galaxy_infos, key=lambda k: k['recyclers_needed'])
        while max_missions > 0:
            max_missions -= 1
            if len(mine_info) > 0:
                recycle = mine_info.pop()
                recyclers_needed = int(recycle["recyclers_needed"])
                if recyclers_needed < min_recyclers or recyclers_needed > max_recyclers:
                    continue
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
                self.ogame.send_fleet(self.id(), ships, speed, where, mission, resources)

    #
    # Build actions
    #

    def build_mines(self):
        info = self.data
        if not info["isUnderConstruction"]:
            mines = dict()
            mines["metal_mine"] = info["buildings"]["metal_mine"]
            mines["crystal_mine"] = info["buildings"]["crystal_mine"]
            mines["deuterium_synthesizer"] = info["buildings"]["deuterium_synthesizer"]
            for m in sorted(mines, key=mines.get):
                if self.ogame.can_build(self.id(), Buildings[m], 'supply'):
                    print("Building %s %d" % (m, mines[m] + 1))
                    self.ogame.build_building(self.id(), Buildings[m])
                    return

    def build_storage(self):
        info = self.data["resources"]
        blds = self.data["buildings"]
        if not self.data["isUnderConstruction"]:
            if info["metal"] >= info["metal_max"] and self.ogame.can_build(self.id(), Buildings["metal_storage"], 'supply'):
                print("Building metal_storage %d" % (blds["metal_storage"] + 1))
                self.ogame.build_building(self.id(), Buildings["metal_storage"])
            elif info["crystal"] >= info["crystal_max"] and self.ogame.can_build(self.id(), Buildings["crystal_storage"], 'supply'):
                print("Building crystal_storage %d" % (blds["crystal_storage"] + 1))
                self.ogame.build_building(self.id(), Buildings["crystal_storage"])
            elif info["deuterium"] >= info["deuterium_max"] and self.ogame.can_build(self.id(), Buildings["deuterium_tank"], 'supply'):
                print("Building deuterium_tank %d" % (blds["deuterium_tank"] + 1))
                self.ogame.build_building(self.id(), Buildings["deuterium_tank"])

    #
    # Fleet actions
    #

    def movement_transport(self, destination, resources=None):
        res = self.data["resources"]
        if resources is None and res["metal"] != {}:
            resources = dict()
            resources["metal"] = res["metal"]
            resources["crystal"] = res["crystal"]
            resources["deuterium"] = res["deuterium"]
        larce_cargoes_needed = 1 + int((resources['metal'] + resources['crystal'] + resources['deuterium']) / 25000)
        ships = [(c.large_cargo, larce_cargoes_needed)]
        speed = Speed['100%']
        destination_coords = destination.data["coordinate"]
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
        self.ogame.send_fleet(self.id(), ships, speed, where, mission, resources)

    def movement_reverse_transport(self, planet, resources=None):
        planet.movement_transport(self.id(), resources)

    def movement_expedition(self, large_cargo_count=200):
        """send expedition with 200 LC"""
        ships = [(c.espionage_probe, 1), (c.large_cargo, large_cargo_count)]
        speed = Speed['100%']
        galaxy = self.ogame.get_planet_infos(self.id())["coordinate"]["galaxy"]
        system = self.ogame.get_planet_infos(self.id())["coordinate"]["system"]
        where = {'galaxy': galaxy, 'system': system, 'position': 16}
        mission = Missions['Expedition']
        resources = {'metal': 0, 'crystal': 0, 'deuterium': 0}

        gen = dict()
        if "available_fleets" not in gen:
            gen.update(self.ogame.get_flying_fleets())
        if gen["available_fleets"] > 0:
            print("Sending %d LC to [%d:%d:%d]" % (large_cargo_count, galaxy, system, 16))
            self.ogame.send_fleet(self.id(), ships, speed, where, mission, resources)
        else:
            return False