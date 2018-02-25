from ogame import OGame
from pprint import pprint as pp
import PrintColor
import json
from helpers import *

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

    def __init__(self):
        print("Account.__init__")

    def login(self, universe, user, password, cookiePath = ""):
        pc.yellow("Logging in with %s" % user, end = " ")

        try:
            self.ogame = OGame(universe, user, password, cookiePath = cookiePath)
        except Exception as e:
           pp.red("Failed to login %s. Exception: " % user + str(e))
        else:
            if self.ogame.is_logged():
                pc.green("Success!")

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

    #TODO: implement print functions

    #
    # Persistance functions
    #

    def load(self, file_name = "ogame.json"):
        """Reads the data from a json file"""
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
            pc.green("Done.")

    def save(self, file_name = "ogame.json"):
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
    # Actions for all the planets
    #

    def do(self):
        for planet in self.planets:
            self.do_actions(planet)

    def do_actions(self, planet):
        planet.fetch_all()
        planet.pp_full()
        planet.fix_energy()
        planet.fix_defense()

    #
    # TODO: name this
    #

    def planet_data(self, planet_id):
        for planet in self.planets:
            if planet.id() == planet_id:
                return planet.data

    #
    # Main loop (do this every time)
    #

    minimum_wait_time = 10
    wait_time = 60

    def loop(self):
        while True:
            self.do()

            # feeling sleepy
            time_to_sleep = random.uniform(self.minimum_wait_time, self.minimum_wait_time + self.wait_time)
            pc.bold("Sleeping %.2f minutes\nZZzzzZz.. zz... zzzZz...\n" % time_to_sleep)
            time.sleep(time_to_sleep * 60)

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

    def fetch(self):
        pc.yellow("Reading %s infos... " % self.name(), end = " ")
        info = dict()
        info.update(self.ogame.get_planet_infos(self.id()))
        info["resources"] = self.ogame.get_resources(self.id())
        info["buildings"] = self.ogame.get_resources_buildings(self.id())
        info["queue"] = self.ogame.get_overview(self.id())
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
        d = self.ogame.get_defense(self.id())
        self.data["defense"] = d
        pc.green("Done!")

    def fetch_facilities(self):
        pc.yellow("Reading %s facilities... " % self.name(), end=" ")
        info = dict()
        info["facilities"] = self.ogame.get_facilities(self.id())
        self.data.update(info)
        pc.green("Done!")

    def fetch_fleet(self):
        pass

    def fetch_all(self):
        self.fetch()
        self.fetch_ships()
        self.fetch_defense()
        self.fetch_facilities()
        self.fetch_fleet()

    #
    # Printing functions (only displays data that was read before)
    #

    def _pp(self, string):
        if "planet_name" not in self.data:
            pc.red("data not fetched.")
            return
        print("%-15s  " % self.data["planet_name"] + string)

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
        pp(self.data["buildings"])

    def pp_facilities(self):
        pp(self.data["facilities"])

    def pp_ships(self):
        pp(self.data["ships"])

    def pp_defense(self):
        pp(self.data["defense"])

    def pp_fleet(self):
        pass

    def pp_full(self):
        self.pp_info()
        self.pp_resources()
        self.pp_buildings()
        self.pp_facilities()
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
                ogame.build_ships(p, c.solar_satellite, int(nr_of_ss))

    def fix_defense(self):
        if "defense_fix" not in self.data:
            pc.red("No `defense_fix` key created for " + self.name())
            return

        current = self.data["defense"]
        target = self.data["defense_fix"]

        for dkey, dcount in current.items():
            if target[dkey] < dcount:
                continue

            dmissing = target[dkey] - dcount - self._shipyard_queue(Defense[dkey])

            if dmissing > 0:
                print("Building %s x%d" % (dkey, dmissing))
                ogame.build_defense(self.id(), Defense[dkey], dmissing)

    def _shipyard_queue(self, item_id):
        queue = self.data["queue"]["shipyard"]
        item_count = 0
        for dictionary in queue:
            if dictionary["code"] == item_id:
                item_count += dictionary["quantity"]
        return item_count

    def get_resources(self, building_str="", level_diff=1):
        res = self.data["resources"]

        cost = {}
        if building_str == "":
            cost['metal'] = 0
            cost['crystal'] = 0
            cost['deuterium'] = 0
        else:
            building_lvl = self.data["buildings"][building_str] + level_diff
            cost = self.ogame.calc_building_cost(building_str, building_lvl)

        missing = dict()
        missing['metal'] = max(0, cost['metal'] - res['metal'])
        missing['crystal'] = max(0, cost['crystal'] - res['crystal'])
        missing['deuterium'] = max(0, cost['deuterium'] - res['deuterium'])

        return missing

    def transport(self, planet_id, resources={}):
        res = self.data["resources"]
        if resources == {} and res["metal"] != {}:
            resources["metal"] = res["metal"]
            resources["crystal"] = res["crystal"]
            resources["deuterium"] = res["deuterium"]
        larce_cargoes_needed = 1 + int((resources['metal'] + resources['crystal'] + resources['deuterium']) / 25000)
        ships = [(c.large_cargo, larce_cargoes_needed)]
        speed = Speed['100%']
        destination_coords = self.acc.planet_data(planet_id)["coordinate"]
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