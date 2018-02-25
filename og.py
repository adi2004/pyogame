from ogame import OGame
from pprint import pprint as pp
import PrintColor
import json
from collections import namedtuple
import sys

pc = PrintColor.PrintColor
pp.red = pc.red

import collections

def merge_dict(new_dict, old_dict):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``old_dict`` is merged into
    ``new_dict``.
    :param new_dict: dict onto which the merge is executed
    :param old_dict: dct merged into dct
    :return: None
    """
    for k, v in old_dict.items():
        if (k in new_dict and isinstance(new_dict[k], dict)
                and isinstance(old_dict[k], collections.Mapping)):
            merge_dict(new_dict[k], old_dict[k])
        else:
            new_dict[k] = old_dict[k]

class Account:
    """The bot contains an instance to the main page of the app"""

    # ogame logic
    ogame = None

    # data dictionary
    data = {}

    # array of planets and moons
    all = []

    def __init__(self):
        print("Init is called")

    def login(self, universe, user, password, cookiePath = ""):
        pc.yellow("Logging in with %s" % user, end = " ")

        try:
            self.ogame = OGame(universe, user, password, cookiePath = cookiePath)
        except Exception as e:
           pp.red("Failed to login %s. Exception: " % user + str(e))
        else:
            if self.ogame.is_logged():
                pc.green("Success!")

    def up_planets(self):
        if self.ogame is None:
            pp.red("Not logged in")
            return

        # read from the server
        pc.yellow("Getting all planet ids...")
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

    def up_account(self):
        if self.ogame is None:
            pp.red("Not logged in")
            return

    def load(self, file_name = "ogame.json"):
        """Reads the data from a json file"""
        try:
            f = open(file_name, "r")
            data = f.read()
            f.close()
            # data = '{"planet": {"mines": "none"}, "moon": {"produciton": "tbd"}}'
            self.data = json.loads(data)
        except Exception as e:
            pp.red("JSON format error: " + str(e))

    def save(self, file_name = "ogame.json"):
        try:
            f = open(file_name, "w")
            f.write(json.dumps(self.data, indent=4))
            f.close()
        except Exception as e:
            pp.red("Something went wrong: " + str(e))

class Planet:
    data = None

    def __init__(self, data):
        self.data = data

    def pp_name(self):
        pp("%5s" % self.data.name)