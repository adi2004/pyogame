from ogame.constants import Ships, Speed, Missions, Buildings, Research, Defense
from ogame.constants import construct as c

import locale
import time

import collections

print("Loading helpers.py...")
class col:
    RED = '\033[91m'
    ORANGE = '\033[93m'
    GREEN = '\033[92m'
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'



def format_number(number, max_capacity = 0):
    current = locale.getlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, 'ro_RO.UTF-8')
    number_string = locale.format('%d', number, True)
    locale.setlocale(locale.LC_ALL, current)

    if max_capacity == 0 and number < 0:
        return col.RED + number_string + col.ENDC
    if max_capacity == 0 and number >= 0:
        return col.GREEN + number_string + col.ENDC
    if number/max_capacity < 0.9:
        return col.GREEN + number_string + col.ENDC
    if number/max_capacity < 1:
        return col.ORANGE + number_string + col.ENDC
    return col.RED + number_string + col.ENDC

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

