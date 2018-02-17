# coding: utf-8
import datetime
import json
import math
import re
import time
import arrow

import requests
import json
import pickle
import random
import os
import inspect
import pickle

from ogame import constants
from ogame.errors import BAD_UNIVERSE_NAME, BAD_DEFENSE_ID, NOT_LOGGED, BAD_CREDENTIALS, CANT_PROCESS, BAD_BUILDING_ID, \
    BAD_SHIP_ID, BAD_RESEARCH_ID
from bs4 import BeautifulSoup
from dateutil import tz
from ogame.util import get_random_user_agent


def get_proxies(port=9050):
    proxies = {
        'http': 'socks5://127.0.0.1:{}'.format(port),
        'https': 'socks5://127.0.0.1:{}'.format(port)
    }

    return proxies


def get_ip():
    url = 'http://ifconfig.me/ip'
    response = requests.get(url, proxies=get_proxies())
    return 'tor ip: {}'.format(response.text.strip())


def parse_int(text):
    try:
        return int(text.replace('.', '').replace(',', '').strip())
    except ValueError:
        return 0


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:  # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, retry_if_logged_out(decorator(getattr(cls, attr))))
        return cls

    return decorate


def sandbox_decorator(some_fn):
    def wrapper(ogame, *args, **kwargs):
        fn_name = some_fn.__name__

        local_fns = ['get_datetime_from_time']

        if fn_name in local_fns:
            return some_fn(ogame, *args, **kwargs)

        if fn_name == '__init__' or not ogame.sandbox:
            return some_fn(ogame, *args, **kwargs)

        if fn_name in ogame.sandbox_obj:
            return ogame.sandbox_obj[fn_name]

        return None

    return wrapper


def retry_if_logged_out(method):
    def wrapper(self, *args, **kwargs):
        attempt = 0
        time_to_sleep = 0
        working = False
        while not working:
            try:
                working = True
                res = method(self, *args, **kwargs)
            except NOT_LOGGED:
                time.sleep(time_to_sleep)
                attempt += 1
                time_to_sleep += 1
                if attempt > 5:
                    raise CANT_PROCESS
                working = False
                self.login()
        return res

    return wrapper


def get_nbr(soup, name):
    div = soup.find('div', {'class': name})
    level = div.find('span', {'class': 'level'})
    for tag in level.findAll(True):
        tag.extract()
    return parse_int(level.text)


def metal_mine_production(level, universe_speed=1):
    return int(math.floor(30 * level * 1.1 ** level) * universe_speed)


def get_planet_infos_regex(text):
    result = re.search(r'(\w+) \[(\d+):(\d+):(\d+)\]([\d\.]+)km \((\d+)/(\d+)\)([-\d]+).+C (?:bis|to) ([-\d]+).+C',
                       text)
    if result is not None:
        return result  # is a plenet
    else:
        return re.search(r'(\w+) \[(\d+):(\d+):(\d+)\]([\d\.]+)km \((\d+)/(\d+)\)', text)  # is a moon


def get_code(name):
    if name in constants.Buildings.keys():
        return constants.Buildings[name]
    if name in constants.Facilities.keys():
        return constants.Facilities[name]
    if name in constants.Defense.keys():
        return constants.Defense[name]
    if name in constants.Ships.keys():
        return constants.Ships[name]
    if name in constants.Research.keys():
        return constants.Research[name]
    print('Couldn\'t find code for {}'.format(name))
    return None


@for_all_methods(sandbox_decorator)
class OGame(object):
    def __init__(self, universe, username, password, domain='en.ogame.gameforge.com', auto_bootstrap=True, sandbox=False, sandbox_obj=None, use_proxy=False, proxy_port=9050, cookiePath="."):
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'})
        self.sandbox = sandbox
        self.sandbox_obj = sandbox_obj if sandbox_obj is not None else {}
        self.universe = universe
        self.domain = domain
        self.username = username
        self.password = password
        self.cookiePath = cookiePath
        self.universe_speed = 1
        self.server_url = ''
        self.server_tz = 'GMT+0'
        if auto_bootstrap:
            self.login()
            self.universe_speed = self.general_get_universe_speed()
        if use_proxy:
            self.session.proxies.update(get_proxies(proxy_port))

    def save_cookies(self, session, filename):
        if not os.path.isdir(os.path.dirname(filename)):
            return False
        with open(filename, 'w') as f:
            f.truncate()
            pickle.dump(session.cookies._cookies, f)

    def load_cookies(self, session, filename):
        if not os.path.isfile(filename):
            return False

        with open(filename) as f:
            try:
                cookies = pickle.load(f)
            except ValueError:
                # ValueError
                cookies = None
                f.truncate()
            if cookies:
                jar = requests.cookies.RequestsCookieJar()
                jar._cookies = cookies
                session.cookies = jar
            else:
                return False

    def login(self):
        """Get the ogame session token."""
        if self.server_url == '':
            self.server_url = self.get_universe_url(self.universe)
        self.load_cookies(self.session, self.cookiePath)
        if not self.is_logged():
            payload = {'kid': '',
                    'uni': self.server_url,
                    'login': self.username,
                    'pass': self.password}
            time.sleep(random.uniform(1, 5))
            res = self.session.post(self.get_url('login'), data=payload).content
            soup = BeautifulSoup(res, 'lxml')
            session_found = soup.find('meta', {'name': 'ogame-session'})
            if session_found:
                self.save_cookies(self.session, self.cookiePath)
                self.ogame_session = session_found.get('content')
            else:
                raise BAD_CREDENTIALS

    def logout(self):
        self.session.get(self.get_url('logout'))
        self.session.cookies.clear()

    def is_logged(self, html=None):
        if not html:
            html = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(html, 'lxml')
        session = soup.find('meta', {'name': 'ogame-session'})
        if session:
            self.ogame_session = html
        return session is not None

    def html_get_page_content(self, page='overview', cp=None):
        """Return the html of a specific page."""
        payload = {}
        if cp is not None:
            payload.update({'cp': cp})
        html = self.session.get(self.get_url(page, payload)).content
        if not self.is_logged(html):
            raise NOT_LOGGED
        return html

    def fetch_eventbox(self):
        res = self.session.get(self.get_url('fetchEventbox')).content.decode('utf8')
        try:
            obj = json.loads(res)
        except ValueError:
            raise NOT_LOGGED
        return obj

    def html_fetch_resources(self, planet_id):
        url = self.get_url('fetchResources', {'cp': planet_id})
        res = self.session.get(url).content.decode('utf8')
        try:
            obj = json.loads(res)
        except ValueError:
            raise NOT_LOGGED
        return obj

    def get_resources(self, planet_id):
        """Returns the planet resources stats."""
        resources = self.html_fetch_resources(planet_id)
        metal = resources['metal']['resources']['actual']
        metal_max = resources['metal']['resources']['max']
        crystal = resources['crystal']['resources']['actual']
        crystal_max = resources['crystal']['resources']['max']
        deuterium  = resources['deuterium']['resources']['actual']
        deuterium_max  = resources['deuterium']['resources']['max']
        energy = resources['energy']['resources']['actual']
        darkmatter = resources['darkmatter']['resources']['actual']
        metal_production = resources['metal']['resources']['production']
        crystal_production = resources['crystal']['resources']['production']
        deuterium_production = resources['crystal']['resources']['production']
        dailyTotalRes = (metal_production + crystal_production + deuterium_production) * 86400
        result = {
            'metal': metal,
            'crystal': crystal,
            'deuterium': deuterium,
            'energy': energy,
            'darkmatter': darkmatter,
            'metal_max': metal_max,
            'crystal_max': crystal_max,
            'deuterium_max': deuterium_max,
            'metal_production': metal_production,
            'crystal_production': crystal_production,
            'deuterium_production': deuterium_production,
            'dailyTotalRes': dailyTotalRes
        }
        return result

    def general_get_universe_speed(self, res=None):
        if not res:
            res = self.session.get(self.get_url('techtree', {'tab': 2, 'techID': 1})).content
        soup = BeautifulSoup(res, 'lxml')
        if soup.find('head'):
            raise NOT_LOGGED
        spans = soup.findAll('span', {'class': 'undermark'})
        level = parse_int(spans[0].text)
        val = parse_int(spans[1].text)
        metal_production = metal_mine_production(level, 1)
        universe_speed = val / metal_production
        return universe_speed

    def get_count_planets(self):
        html = self.session.get(self.get_url('overview')).content
        if not self.is_logged(html):
            raise NOT_LOGGED
        soup = BeautifulSoup(html, 'lxml')
        link = soup.find('div', {'id': 'countColonies'})
        res = {}
        if link is not None:
            link = link.find('span').text
            infos = re.search(r'(\d+)\/(\d+)', link)
            res['colonies_count'] = parse_int(infos.group(1))
            res['colonies_maxcount'] = parse_int(infos.group(2))
            return res


    def general_get_user_infos(self, html=None):
        if not html:
            html = self.session.get(self.get_url('overview')).content
        if not self.is_logged(html):
            raise NOT_LOGGED
        res = {}
        res['player_id'] = int(re.search(r'playerId="(\w+)"', str(html)).group(1))
        res['player_name'] = re.search(r'playerName="([\w\s]+)"', str(html)).group(1)
        tmp = re.search(r'textContent\[7\]="([^"]+)"', str(html)).group(1)
        soup = BeautifulSoup(tmp, 'lxml')
        tmp = soup.text
        infos = re.search(r'([\d\\.]+) \(\S+ ([\d\.]+) \S+ ([\d\.]+)\)', tmp)
        res['points'] = parse_int(infos.group(1))
        res['rank'] = parse_int(infos.group(2))
        res['total'] = parse_int(infos.group(3))
        res['honour_points'] = parse_int(re.search(r'textContent\[9\]="([^"]+)"', str(html)).group(1))
        res['planet_ids'] = self.get_planet_ids(html)
        res['current_planets'] = re.search(r'(\d+)/(\d+)',
                                           BeautifulSoup(html, 'lxml').find('p', 'textCenter').text).group(1)
        res['max_planets'] = re.search(r'(\d+)/(\d+)',
                                       BeautifulSoup(html, 'lxml').find('p', 'textCenter').text).group(2)
        return res

    def get_resources_buildings(self, planet_id):
        res = self.session.get(self.get_url('resources', {'cp': planet_id})).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        res = {}
        res['metal_mine'] = get_nbr(soup, 'supply1')
        res['crystal_mine'] = get_nbr(soup, 'supply2')
        res['deuterium_synthesizer'] = get_nbr(soup, 'supply3')
        res['solar_plant'] = get_nbr(soup, 'supply4')
        res['fusion_reactor'] = get_nbr(soup, 'supply12')
        res['solar_satellite'] = get_nbr(soup, 'supply212')
        res['metal_storage'] = get_nbr(soup, 'supply22')
        res['crystal_storage'] = get_nbr(soup, 'supply23')
        res['deuterium_tank'] = get_nbr(soup, 'supply24')
        return res

    def get_defense(self, planet_id):
        res = self.session.get(self.get_url('defense', {'cp': planet_id})).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        res = {}
        res['rocket_launcher'] = get_nbr(soup, 'defense401')
        res['light_laser'] = get_nbr(soup, 'defense402')
        res['heavy_laser'] = get_nbr(soup, 'defense403')
        res['gauss_cannon'] = get_nbr(soup, 'defense404')
        res['ion_cannon'] = get_nbr(soup, 'defense405')
        res['plasma_turret'] = get_nbr(soup, 'defense406')
        res['small_shield_dome'] = get_nbr(soup, 'defense407')
        res['large_shield_dome'] = get_nbr(soup, 'defense408')
        res['anti_ballistic_missiles'] = get_nbr(soup, 'defense502')
        res['interplanetary_missiles'] = get_nbr(soup, 'defense503')
        return res

    def get_ships(self, planet_id):
        res = self.session.get(self.get_url('shipyard', {'cp': planet_id})).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        res = {}
        res['light_fighter'] = get_nbr(soup, 'military204')
        res['heavy_fighter'] = get_nbr(soup, 'military205')
        res['cruiser'] = get_nbr(soup, 'military206')
        res['battleship'] = get_nbr(soup, 'military207')
        res['battlecruiser'] = get_nbr(soup, 'military215')
        res['bomber'] = get_nbr(soup, 'military211')
        res['destroyer'] = get_nbr(soup, 'military213')
        res['deathstar'] = get_nbr(soup, 'military214')
        res['small_cargo'] = get_nbr(soup, 'civil202')
        res['large_cargo'] = get_nbr(soup, 'civil203')
        res['colony_ship'] = get_nbr(soup, 'civil208')
        res['recycler'] = get_nbr(soup, 'civil209')
        res['espionage_probe'] = get_nbr(soup, 'civil210')
        res['solar_satellite'] = get_nbr(soup, 'civil212')
        return res

    def get_facilities(self, planet_id):
        res = self.session.get(self.get_url('station', {'cp': planet_id})).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        res = {}
        res['robotics_factory'] = get_nbr(soup, 'station14')
        res['shipyard'] = get_nbr(soup, 'station21')
        res['research_lab'] = get_nbr(soup, 'station31')
        res['alliance_depot'] = get_nbr(soup, 'station34')
        res['missile_silo'] = get_nbr(soup, 'station44')
        res['nanite_factory'] = get_nbr(soup, 'station15')
        res['terraformer'] = get_nbr(soup, 'station33')
        res['space_dock'] = get_nbr(soup, 'station36')
        return res

    def get_research(self):
        res = self.session.get(self.get_url('research')).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        res = {}
        res['energy_technology'] = get_nbr(soup, 'research113')
        res['laser_technology'] = get_nbr(soup, 'research120')
        res['ion_technology'] = get_nbr(soup, 'research121')
        res['hyperspace_technology'] = get_nbr(soup, 'research114')
        res['plasma_technology'] = get_nbr(soup, 'research122')
        res['combustion_drive'] = get_nbr(soup, 'research115')
        res['impulse_drive'] = get_nbr(soup, 'research117')
        res['hyperspace_drive'] = get_nbr(soup, 'research118')
        res['espionage_technology'] = get_nbr(soup, 'research106')
        res['computer_technology'] = get_nbr(soup, 'research108')
        res['astrophysics'] = get_nbr(soup, 'research124')
        res['intergalactic_research_network'] = get_nbr(soup, 'research123')
        res['graviton_technology'] = get_nbr(soup, 'research199')
        res['weapons_technology'] = get_nbr(soup, 'research109')
        res['shielding_technology'] = get_nbr(soup, 'research110')
        res['armour_technology'] = get_nbr(soup, 'research111')
        return res

    def is_under_attack(self, json_obj=None):
        if not json_obj:
            json_obj = self.fetch_eventbox()
        return not json_obj.get('hostile', 0) == 0

    def get_planet_ids(self, res=None):
        """Get the ids of your planets."""
        if not res:
            res = self.session.get(self.get_url('overview')).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        planets = soup.findAll('div', {'class': 'smallplanet'})
        ids = [planet['id'].replace('planet-', '') for planet in planets]
        return ids

    def get_moon_ids(self, res=None):
        """Get the ids of your moons."""
        if not res:
            res = self.session.get(self.get_url('overview')).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        moons = soup.findAll('a', {'class': 'moonlink'})
        ids = [moon['href'].split('&cp=')[1] for moon in moons]
        return ids

    def get_planet_by_name(self, planet_name, res=None):
        """Returns the first planet id with the specified name."""
        if not res:
            res = self.session.get(self.get_url('overview')).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        planets = soup.findAll('div', {'class': 'smallplanet'})
        for planet in planets:
            title = planet.find('a', {'class': 'planetlink'}).get('title')
            name = re.search(r'<b>(.+) \[(\d+):(\d+):(\d+)\]</b>', title).groups()[0]
            if name == planet_name:
                planet_id = planet['id'].replace('planet-', '')
                return planet_id
        return None

    def build_defense(self, planet_id, defense_id, nbr):
        """Build a defense unit."""
        print("builddef")
        if defense_id not in constants.Defense.values():
            print("baddef")
            raise BAD_DEFENSE_ID

        url = self.get_url('defense', {'cp': planet_id})

        res = self.session.get(url).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'menge': nbr,
                   'modus': 1,
                   'token': token,
                   'type': defense_id}
        print("def post")
        self.session.post(url, data=payload)

    def get_shipyard_queue_size(self, planet_id):
        """Build a ship unit."""

        url = self.get_url('shipyard', {'cp': planet_id})

        res = self.session.get(url).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        items = soup.find_all("li", {"class": "tooltip"})
        return items.__len__()

    def get_shipyard_queue(self, planet_id):
        """Build a ship unit."""

        url = self.get_url('shipyard', {'cp': planet_id})

        res = self.session.get(url).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        items = soup.find_all("li", {"class": "tooltip"})
        resultList = []

        nowOnItems = soup.find("td", {"class": "building tooltip"})
        if nowOnItems == None:
            return resultList

        items.insert(0, nowOnItems)

        for item in items:
            resultDict = {}
            if item == None:
                continue;

            itemCount = item.span.string if item.span != None else item.div.string
            itemID = item.a.get('ref')

            if itemID is None:
                itemID = item.a.get('href').split('openTech=')[1]
            resultDict.update({'id': itemID})
            resultDict.update({'count': itemCount})

            if item.attrs['class'][0] == "building":
                resultDict.update({'onProgress': True})
            else:
                resultDict.update({'onProgress': False})

            resultList.append(resultDict)

        return resultList

    def build_ships(self, planet_id, ship_id, nbr):
        """Build a ship unit."""
        if ship_id not in constants.Ships.values():
            raise BAD_SHIP_ID

        url = self.get_url('shipyard', {'cp': planet_id})

        res = self.session.get(url).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'menge': nbr,
                   'modus': 1,
                   'token': token,
                   'type': ship_id}
        self.session.post(url, data=payload)

    def can_build(self, costs, planet_resources):
        if planet_resources['metal'] >= costs[0] and planet_resources['crystal'] >= costs[1] and planet_resources['deuterium'] >= costs[2]:
            return True
        return False

    def build_building(self, planet_id, building_id, cancel=False):
        """Build a building."""
        if building_id not in constants.Buildings.values() and building_id not in constants.Facilities.values():
            raise BAD_BUILDING_ID

        url = self.get_url('resources', {'cp': planet_id})

        res = self.session.get(url).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        # is_idle = bool(soup.find('td', {'class': 'idle'}))
        # if not is_idle:
        #     return False
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')
        modus = 2 if cancel else 1
        payload = {'modus': modus,
                   'token': token,
                   'type': building_id}
        self.session.post(url, data=payload)
        # return True

    def build_technology(self, planet_id, technology_id, cancel=False):
        if technology_id not in constants.Research.values():
            raise BAD_RESEARCH_ID

        url = self.get_url('research', {'cp': planet_id})
        modus = 2 if cancel else 1
        payload = {'modus': modus,
                   'type': technology_id}
        res = self.session.post(url, data=payload).content
        if not self.is_logged(res):
            raise NOT_LOGGED

    def _build(self, planet_id, object_id, nbr=None, cancel=False):
        if object_id in constants.Buildings.values() or object_id in constants.Facilities.values():
            self.build_building(planet_id, object_id, cancel=cancel)
        elif object_id in constants.Research.values():
            self.build_technology(planet_id, object_id, cancel=cancel)
        elif object_id in constants.Ships.values():
            self.build_ships(planet_id, object_id, nbr)
        elif object_id in constants.Defense.values():
            self.build_defense(planet_id, object_id, nbr)

    def build(self, planet_id, arg, cancel=False):
        if isinstance(arg, list):
            for element in arg:
                self.build(planet_id, element, cancel=cancel)
        elif isinstance(arg, tuple):
            elem_id, nbr = arg
            self._build(planet_id, elem_id, nbr, cancel=cancel)
        else:
            elem_id = arg
            self._build(planet_id, elem_id, cancel=cancel)

    def send_fleet(self, planet_id, ships, speed, where, mission, resources, acsDefHoldTime=0):
        def get_hidden_fields(html):
            soup = BeautifulSoup(html, 'lxml')
            inputs = soup.findAll('input', {'type': 'hidden'})
            fields = {}
            for input_element in inputs:
                name = input_element.get('name')
                value = input_element.get('value')
                fields[name] = value
            return fields

        url = self.get_url('fleet1', {'cp': planet_id})

        res = self.session.get(url).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        payload = {}
        payload.update(get_hidden_fields(res))
        for name, value in ships:
            payload['am{}'.format(name)] = value
        res = self.session.post(self.get_url('fleet2'), data=payload).content

        payload = {}
        payload.update(get_hidden_fields(res))
        payload.update({'speed': speed,
                        'galaxy': where.get('galaxy'),
                        'system': where.get('system'),
                        'position': where.get('position'),
                        'type': where.get('type', 1)})

        res = self.session.post(self.get_url('fleet3'), data=payload).content

        payload = {}
        payload.update(get_hidden_fields(res))
        payload.update({'crystal': resources.get('crystal'),
                        'deuterium': resources.get('deuterium'),
                        'metal': resources.get('metal'),
                        'mission': mission,
                        'holdingtime': acsDefHoldTime
                        })
        res = self.session.post(self.get_url('movement'), data=payload).content

        res = self.session.get(self.get_url('movement')).content
        soup = BeautifulSoup(res, 'lxml')
        origin_coords = soup.find('meta', {'name': 'ogame-planet-coordinates'})['content']
        fleets = soup.findAll('div', {'class': 'fleetDetails'})
        matches = []
        for fleet in fleets:
            origin = fleet.find('span', {'class': 'originCoords'}).text
            dest = fleet.find('span', {'class': 'destinationCoords'}).text
            reversal_span = fleet.find('span', {'class': 'reversal'})
            if not reversal_span:
                continue
            fleet_id = int(reversal_span.get('ref'))
            if dest == '[{}:{}:{}]'.format(where['galaxy'], where['system'],
                                           where['position']) and origin == '[{}]'.format(origin_coords):
                matches.append(fleet_id)
        if matches:
            return max(matches)
        return None

    def cancel_fleet(self, fleet_id):
        res = self.session.get(self.get_url('movement') + '&return={}'.format(fleet_id)).content
        if not self.is_logged(res):
            raise NOT_LOGGED

    def get_flight_duration(self, Geschwindigkeitsfaktor, Entfernung, GeschwindigkeitDesLangsamstenSchiffs, UniFleetSpeed=1):
        #Flugzeit in Sekunden:
        #= (3.500 / Geschwindigkeitsfaktor) * (Entfernung * 10 / GeschwindigkeitDesLangsamstenSchiffs) ^ 0,5 + 10
        duration = ((3500 / Geschwindigkeitsfaktor) * (Entfernung * 10 /
                                                       GeschwindigkeitDesLangsamstenSchiffs) ** 0.5 + 10) / UniFleetSpeed

        return duration

    def get_flight_distance(self, origin_galaxy, origin_system, origin_position, target_galaxy, target_system, target_position):
        if origin_galaxy != target_galaxy:
            return math.fabs(origin_galaxy - target_galaxy) * 20000
        elif origin_system != target_system:
            return math.fabs(origin_system - target_system) * 95 + 2700
        elif origin_position != target_position:
            return math.fabs(origin_position - target_position) * 5 + 1000
        else:
            return 5

    def get_fleet_slots(self):
        res = self.session.get(self.get_url('fleet1')).content
        soup = BeautifulSoup(res, 'lxml')
        fleetStatus = soup.find('div', {'class': 'fleetStatus'}).text.strip(
        ).replace(" ", "").replace("\n", "")
        infos = re.search(
            r'(?:Flotten:)(\d+)\/(\d+)(?:Expeditionen:)(\d+)\/(\d+)', fleetStatus)
        return [int(infos.group(1)), int(infos.group(2))]

    def get_fleets(self):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        res = self.session.get(self.get_url('eventList'), params={'ajax': 1},
                               headers=headers).content
        soup = BeautifulSoup(res, 'lxml')
        if soup.find('head'):
            raise NOT_LOGGED
        events = soup.findAll('tr', {'class': 'eventFleet'})
        events = filter(
            lambda x: 'partnerInfo' not in x.get('class', []), events)

        missions = []
        for event in events:
            mission_type = int(event['data-mission-type'])
            mission = {}
            mission.update({'mission_type': mission_type})

            return_flight = event['data-return-flight']
            mission.update({'return_flight': return_flight})

            id = str(event['id'])
            #id = self.get_event_id(str(event['id']))
            mission.update({'id': id})

            coords_origin = event.find('td', {'class': 'coordsOrigin'}) \
                .text.strip()
            coords = re.search(r'\[(\d+):(\d+):(\d+)\]', coords_origin)
            galaxy, system, position = coords.groups()
            mission.update(
                {'origin': (int(galaxy), int(system), int(position))})

            dest_coords = event.find(
                'td', {'class': 'destCoords'}).text.strip()
            coords = re.search(r'\[(\d+):(\d+):(\d+)\]', dest_coords)
            galaxy, system, position = coords.groups()
            mission.update(
                {'destination': (int(galaxy), int(system), int(position))})

            arrival_time = event.find(
                'td', {'class': 'arrivalTime'}).text.strip()
            coords = re.search(r'(\d+):(\d+):(\d+)', arrival_time)

            hour, minute, second = coords.groups()
            hour = int(hour)
            minute = int(minute)
            second = int(second)
            arrival_time = self.get_datetime_from_time(hour, minute, second)
            mission.update({'arrival_time': arrival_time})

            if mission_type == 1:
                attacker_id = event.find('a', {'class': 'sendMail'})[
                    'data-playerid']
                mission.update({'attacker_id': int(attacker_id)})
            else:
                mission.update({'attacker_id': None})

            missions.append(mission)
        return missions

    def get_fleet_ids(self):
        """Return the reversable fleet ids."""
        res = self.session.get(self.get_url('movement')).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        spans = soup.findAll('span', {'class': 'reversal'})
        fleet_ids = [span.get('ref') for span in spans]
        return fleet_ids

    def get_attacks(self, checkSpyAlso=False):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        res = self.session.get(self.get_url('eventList'), params={'ajax': 1},
                               headers=headers).content
        soup = BeautifulSoup(res, 'lxml')
        if soup.find('head'):
            raise NOT_LOGGED
        events = soup.findAll('tr', {'class': 'eventFleet'})
        eventsDup = filter(lambda x: 'partnerInfo' not in x.get('class', []), events)
        events = soup.findAll('tr', {'class': 'allianceAttack'})
        events += eventsDup
        # unsupported operand type(s) for +=: 'filter' and 'ResultSet'


        attacks = []
        for event in events:
            mission_type = int(event['data-mission-type'])

            if mission_type not in [1, 2, 9, 6]:
                continue

            if mission_type not in [1, 2]:
                if checkSpyAlso and mission_type not in [6]:
                    continue
                elif checkSpyAlso is False:
                    continue
                else:
                    None

            attack = {}
            attack.update({'mission_type': mission_type})
            if mission_type == 1:
                coords_origin = event.find('td', {'class': 'coordsOrigin'}) \
                    .text.strip()
                coords = re.search(r'\[(\d+):(\d+):(\d+)\]', coords_origin)
                galaxy, system, position = coords.groups()
                attack.update({'origin': (int(galaxy), int(system), int(position))})

                # CHECK IF IT IS HOSTILE
                is_hostile = False
                check_hostile = event.find('td', {'class': 'hostile'})
                if check_hostile is not None:
                    is_hostile = True
                attack.update({'is_hostile': is_hostile})
            elif mission_type == 6:
                total_fleet = event.find('td', {'class': 'icon_movement'})
                if total_fleet is None:
                    None
                else:
                    total_fleet = total_fleet.find('span')['title']
                    soup_fleet = BeautifulSoup(total_fleet, 'lxml')
                    total_tr = len(soup_fleet.findAll('tr'))
                    if total_tr > 2:
                        attack.update({'origin': None})
                        attack.update({'is_hostile': True})
                    else:
                        attack.update({'origin': None})
                        attack.update({'is_hostile': False})
            elif mission_type == 9:
                attack.update({'origin': None})
                attack.update({'is_hostile': True})
            else:
                attack.update({'origin': None})
                attack.update({'is_hostile': True})

            dest_moon = event.find('td', {'class': 'destFleet'}).find('figure',
                                                                      {'class': 'planetIcon moon'}) is not None

            attack.update(({'is_toMoon': dest_moon}))
            dest_coords = event.find('td', {'class': 'destCoords'}).text.strip()
            coords = re.search(r'\[(\d+):(\d+):(\d+)\]', dest_coords)
            galaxy, system, position = coords.groups()
            attack.update({'destination': (int(galaxy), int(system), int(position))})

            arrival_time = event.find('td', {'class': 'arrivalTime'}).text.strip()
            coords = re.search(r'(\d+):(\d+):(\d+)', arrival_time)
            hour, minute, second = coords.groups()
            hour = int(hour)
            minute = int(minute)
            second = int(second)
            arrival_time = self.get_datetime_from_time(hour, minute, second)
            attack.update({'arrival_time': arrival_time})

            # todo Mn replace 제대로
            # attack.update({'detailsFleet': int(event.find('td', {'class': 'detailsFleet'}).text.replace(".","").replace("Mn","").strip())})
            try:
                attack.update({'detailsFleet': int(event.find('td', {'class': 'detailsFleet'}).text.strip())})
            except ValueError as ve:
                attack.update({'detailsFleet': "(?)"})

            if mission_type == 1:
                attacker_id = event.find('a', {'class': 'sendMail'})['data-playerid']
                attack.update({'attacker_id': int(attacker_id)})
            else:
                attack.update({'attacker_id': None})

            attacks.append(attack)
        return attacks

    def get_datetime_from_time(self, hour, minute, second):
        attack_time = arrow.utcnow().to(self.server_tz).replace(hour=hour, minute=minute, second=second)
        now = arrow.utcnow().to(self.server_tz)
        if now.hour > attack_time.hour:
            attack_time += datetime.timedelta(days=1)
        return attack_time.to(tz.tzlocal()).datetime

    def get_url(self, page, params=None):
        if params is None:
            params = {}
        if page == 'login':
            return 'https://{}/main/login'.format(self.domain)
        else:
            timeout = random.randrange(100, 300)
            # print "Waiting " + str(timeout) + "ms"
            time.sleep(timeout / 1000.0)

            if self.server_url == '':
                self.server_url = self.get_universe_url(self.universe)
            url = 'https://{}/game/index.php?page={}'.format(self.server_url, page)
            if params:
                arr = []
                for key in params:
                    arr.append("{}={}".format(key, params[key]))
                url += '&' + '&'.join(arr)
            return url

    def get_servers(self, domain):
        res = self.session.get('https://{}'.format(domain)).content
        soup = BeautifulSoup(res, 'lxml')
        select = soup.find('select', {'id': 'serverLogin'})
        servers = {}
        for opt in select.findAll('option'):
            url = opt.get('value')
            name = opt.string.strip().lower()
            servers[name] = url
        return servers

    def get_universe_url(self, universe):
        """Get a universe name and return the server url."""
        servers = self.get_servers(self.domain)
        universe = universe.lower()
        if universe not in servers:
            raise BAD_UNIVERSE_NAME
        return servers[universe]

    def get_server_time(self):
        """Get the ogame server time."""
        res = self.session.get(self.get_url('overview')).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        date_str = soup.find('li', {'class': 'OGameClock'}).text
        date_format = '%d.%m.%Y %H:%M:%S'
        date = datetime.datetime.strptime(date_str, date_format)
        return date

    def get_planet_infos(self, planet_id, res=None):
        if not res:
            res = self.session.get(self.get_url('overview', {'cp': planet_id})).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        link = soup.find('div', {'id': 'planet-{}'.format(planet_id)})
        if link is not None:  # is a planet pid
            link = link.find('a')
        else:  # is a moon pid
            link = soup.find('div', {'id': 'planetList'})
            link = link.find_all('a', {'class': 'moonlink'})
            for node in link:
                nodeContent = node['title']
                if nodeContent.find("cp=" + planet_id) > -1:
                    link = node
                    break
                else:
                    continue

        infos_label = BeautifulSoup(link['title'], 'lxml').text
        infos = get_planet_infos_regex(infos_label)
        isUnderConstruction = soup.find('table', {'class': "construction active"}).find('td', {'class': "desc timer"})
        if isUnderConstruction is None:
            isUnderConstruction = False
        else:
            isUnderConstruction = True

        res = {}
        res['img'] = link.find('img').get('src')
        res['id'] = planet_id
        res['planet_name'] = infos.group(1)
        res['coordinate'] = {}
        res['coordinate']['galaxy'] = int(infos.group(2))
        res['coordinate']['system'] = int(infos.group(3))
        res['coordinate']['position'] = int(infos.group(4))
        res['coordinate']['as_string'] = str(
            res['coordinate']['galaxy']) + ":" + str(res['coordinate']['system']) + ":" + str(res['coordinate']['position'])
        res['diameter'] = parse_int(infos.group(5))
        res['fields'] = {}
        res['fields']['built'] = int(infos.group(6))
        res['fields']['total'] = int(infos.group(7))
        res['temperature'] = {}
        res['isUnderConstruction'] = isUnderConstruction
        if infos.groups().__len__() > 7:  # is a planet
            res['temperature']['min'] = int(infos.group(8))
            res['temperature']['max'] = int(infos.group(9))
        return res

    def general_get_ogame_version(self, res=None):
        """Get ogame version on your server."""
        if not res:
            res = self.session.get(self.get_url('overview')).content
        if not self.is_logged(res):
            raise NOT_LOGGED
        soup = BeautifulSoup(res, 'lxml')
        footer = soup.find('div', {'id': 'siteFooter'})
        version = footer.find('a').text.strip()
        return version

    def get_overview(self, planet_id):
        html = self.session.get(self.get_url('overview', {'cp': planet_id})).content
        if not self.is_logged(html):
            raise NOT_LOGGED
        soup = BeautifulSoup(html, 'lxml')
        boxes = soup.findAll('div', {'class': 'content-box-s'})
        res = {}
        names = ['buildings', 'research', 'shipyard']
        for idx, box in enumerate(boxes):
            is_idle = box.find('td', {'class': 'idle'}) is not None
            res[names[idx]] = []
            if not is_idle:
                name = box.find('th').text #.encode('utf8')
                short_name = ''.join(name.split())
                code = get_code(short_name)
                desc = box.find('td', {'class': 'desc'}).text
                desc = ' '.join(desc.split())
                tmp = [{'name': short_name, 'code': code}]
                if idx == 2:
                    quantity = parse_int(box.find('div', {'id': 'shipSumCount7'}).text)
                    tmp[0].update({'quantity': quantity})
                    queue = box.find('table', {'class': 'queue'})
                    if queue:
                        tds = queue.findAll('td')
                        for td_element in tds:
                            link = td_element.find('a')
                            quantity = parse_int(link.text)
                            img = td_element.find('img')
                            alt = img['alt']
                            short_name = ''.join(alt.split()) #.encode('utf-8')
                            code = get_code(short_name)
                            tmp.append({'name': short_name, 'code': code, 'quantity': quantity})
                res[names[idx]] = tmp
        return res

    def get_resource_settings(self, planet_id):
        html = self.session.get(self.get_url('resourceSettings', {'cp': planet_id})).content
        if not self.is_logged(html):
            raise NOT_LOGGED
        soup = BeautifulSoup(html, 'lxml')
        options = soup.find_all('option', {'selected': True})
        res = {}
        res['metal_mine'] = options[0]['value']
        res['crystal_mine'] = options[1]['value']
        res['deuterium_synthesizer'] = options[2]['value']
        res['solar_plant'] = options[3]['value']
        res['fusion_reactor'] = options[4]['value']
        res['solar_satellite'] = options[5]['value']
        return res

    def send_message(self, player_id, msg):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        payload = {'playerId': player_id,
                   'text': msg,
                   'mode': 1,
                   'ajax': 1}
        url = self.get_url('ajaxChat')
        self.session.post(url, data=payload, headers=headers)

    def getSolarPlantProduction(level=1, Ingenieur = False):
        IngenieurBonus = 1.0
        if Ingenieur:
            IngenieurBonus = 1.1
        return round( math.fabs(20 * level * 1.1 ** level ) * IngenieurBonus)

    def get_solarSatelliteProduction(self, planet_max_temp, satellite_count = 1, Ingenieur = False):
        IngenieurBonus = 1.0

        if Ingenieur:
            IngenieurBonus = 1.1

        return round(math.fabs((planet_max_temp + 140) / 6) * satellite_count * IngenieurBonus)


    def html_galaxy_content(self, galaxy, system):
        headers = {'X-Requested-With': 'XMLHttpRequest',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        payload = {'galaxy': galaxy, 'system': system}
        url = self.get_url('galaxyContent', {'ajax': 1})
        res = self.session.post(url, data=payload, headers=headers).content.decode('utf8')
        try:
            obj = json.loads(res)
        except ValueError:
            raise NOT_LOGGED
        return obj

    def galaxy_infos_new(self, galaxy, system):
        html = self.html_galaxy_content(galaxy, system)['galaxy']
        soup = BeautifulSoup(html, 'lxml')
        rows = soup.findAll('tr', {'class': 'row'})
        res = []
        for position, row in enumerate(rows):
            player_obj = {'player': None, 'galaxy': galaxy, 'system': system, 'position': position + 1, 'status': 'a',
                          'planet': None, 'moon': None, 'debris': None}
            if 'empty_filter' in row.get('class'):
                res.append(player_obj)
                continue

            if 'empty_filter' not in row.get('class'):
                player_obj['player'] = 'Occupied'

            res.append(player_obj)

        return res

    def find_empty_slots(self, html):
        soup = BeautifulSoup(html, 'lxml')
        empty_rows = soup.find_all('tr', {'class': 'empty_filter'})
        empty_positions = []
        if empty_rows is None:
            return empty_positions
        for empty_row in empty_rows:
            empty_positions.append(empty_row.find('td', {'position'}).text)

        return empty_positions

    def html_spy_reports(self):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        payload = {'tab': 20,
                   'ajax': 1}
        url = self.get_url('messages', payload)
        res = self.session.get(url).content.decode('utf8')
        return res

    def delete_spy_reports(self, message_id):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        payload = {'messageId': message_id, 'action': 103, 'ajax': 1}
        url = self.get_url('messages')
        res = self.session.post(url, data=payload, headers=headers).content.decode('utf8')

        return res



    def get_flying_fleets(self):
        url = self.get_url('movement')
        res = self.session.get(url).content
        soup = BeautifulSoup(res, 'lxml')
        current_fleets = soup.find('span', {
            'class': 'current'})
        max_fleets = soup.find('span', {
            'class': 'all'})
        if current_fleets is None:
            text_fleets = soup.find('span', {'class': 'tooltip advice'}).contents[1]
            current_fleets = int(text_fleets.split('/')[0])
            max_fleets = int(text_fleets.split('/')[1])
            available_fleets = max_fleets - current_fleets
            fleet_dict = {'current_fleets': current_fleets, 'max_fleets': max_fleets,
                          'available_fleets': available_fleets}
            return fleet_dict
        current_fleets = int(current_fleets.contents[0])
        max_fleets = int(max_fleets.contents[0])
        available_fleets = max_fleets - current_fleets
        fleet_dict = {'current_fleets': current_fleets, 'max_fleets': max_fleets, 'available_fleets': available_fleets}
        return fleet_dict

    def jumpgate_execute(self):
        res = self.session.get(self.get_url('jumpgate_execute')).content
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return True

    def send_minifleet_spy(self, where, ship_count, token):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        payload = {'mission': 6,
                   'galaxy': where.get('galaxy'),
                   'system': where.get('system'),
                   'position': where.get('position'),
                   'type': 1,
                   'shipCount': ship_count,
                   'token': token,
                   'speed': 10
                   }
        res = self.session.post(self.get_url('minifleet'), params={'ajax': 1}, headers=headers, data=payload).content
        try:
            json_response = json.loads(res)
        except ValueError:
            # from send_message import send_message
            # send_message(
            #     'No se pudo espiar a {}:{}:{}'.format(where.get('galaxy'), where.get('system'), where.get('position')))
            return None
        res_dict = json_response.get('response').get('success')
        if res_dict:
            return 'Sended spy probes'
        return None

    def get_minifleet_token(self, html):
        token = None
        moon_soup = BeautifulSoup(html, 'html.parser')
        data = moon_soup.find_all('script', {'type': 'text/javascript'})
        parameter = 'miniFleetToken'
        for d in data:
            d = d.text
            if 'var miniFleetToken=' in d:
                regex_string = 'var {parameter}="(.*?)"'.format(parameter=parameter)
                token = re.findall(regex_string, d)

        return token

    def check_new_messages(self, html):
        total_messages = 0
        soup = BeautifulSoup(html, 'lxml')
        messages = soup.find('span', {'class': 'totalChatMessages'})
        if messages is not None:
            total_messages = int(messages.attrs['data-new-messages'])

        return total_messages

    def get_new_messages(self):
        msg_list = []
        html = self.session.get(self.get_url('chat')).content
        soup = BeautifulSoup(html, 'lxml')
        new_chats = soup.find('ul', {'id': 'chatMsgList'}).findAll('li', {'class': 'msg_new'})
        if new_chats is None:
            return None
        for chat in new_chats:
            message = ''
            player = ''
            try:
                message = chat.find('span', {'class': 'msg_content'}).contents[0]
                player = chat.find('span', {'class': 'msg_title'}).contents[2]
            except UnicodeEncodeError:
                print('Error getting messages')
            msg = {'message': message.encode('utf-8'), 'player': player.encode('utf-8')}
            msg_list.append(msg)

        return msg_list

    def can_build(self, planet_id, building, building_type):
        building_url = building_type
        if building_type == 'supply':
            building_url = 'resources'

        html = self.session.get(self.get_url(building_url, {'cp': planet_id})).content
        soup = BeautifulSoup(html, 'lxml')
        item_div = soup.find('div', {'class': '{}{}'.format(building_type, building)})
        is_free = item_div.find('a', {'class': 'fastBuild'})
        if is_free is not None:
            return True
        else:
            return False

    def can_build_defenses(self, planet_id, defense_item):
        html = self.session.get(self.get_url('defense', {'cp': planet_id})).content
        defense_code = constants.Defense[defense_item]
        soup = BeautifulSoup(html, 'lxml')
        in_construction = soup.find('div', {'class': 'defense{}'.format(defense_code)}).find('div',
                                                                                             {'class': 'construction'})
        parent_class = soup.find('div', {'class': 'defense{}'.format(defense_code)}).parent.attrs['class']
        if in_construction is not None or parent_class == 'off':
            return False
        else:
            return True

    def can_build_ships(self, planet_id, ship_item):
        html = self.session.get(self.get_url('shipyard', {'cp': planet_id})).content
        ship_code = constants.Ships[ship_item]
        soup = BeautifulSoup(html, 'lxml')
        ship_type = 'civil'

        # get the type of ship
        if ship_code in [204, 205, 206, 207, 213, 214, 215, 211]:
            ship_type = 'military'

        in_construction = soup.find('div', {'class': '{}{}'.format(ship_type, ship_code)}).find('div', {
            'class': 'construction'})
        parent_class = soup.find('div', {'class': '{}{}'.format(ship_type, ship_code)}).parent.attrs['class']
        if in_construction is not None or parent_class == 'off':
            return False
        else:
            return True

    def can_build_research(self, building):
        html = self.session.get(self.get_url('research')).content
        soup = BeautifulSoup(html, 'lxml')
        is_free = soup.find('div', {'class': 'research{}'.format(building)}).find('a', {'class': 'fastBuild'})
        if is_free is not None:
            return True
        else:
            return False

    def alliance_apply(self, alliance_id, message):
        url = self.get_url('allianceWriteApplication', {'action': 1})
        payload = {'text': message,
                   'appliedAllyId': alliance_id}
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        res = self.session.post(url, headers=headers, data=payload).content

    def general_get_ip(self):
        res = self.session.get('http://ifconfig.me/ip')
        return 'ip session: {}'.format(res.text.strip())

    def delete_planet(self, planet_id):
        html = self.session.get(self.get_url('planetlayer')).content
        soup = BeautifulSoup(html, 'lxml')
        form = soup.find('form', {'id': 'planetMaintenanceDelete'})
        abandon = form.find('input', {'name': 'abandon'}).get('value')
        token = form.find('input', {'name': 'token'}).get('value')
        payload = {'abandon': abandon,
                   'token': token,
                   'password': self.password}
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        check_password = self.session.post(self.get_url('checkPassword'), headers=headers, data=payload).content
        jo = json.loads(check_password)
        new_token = jo['newToken']
        delete_payload = {'abandon': abandon,
                          'token': new_token,
                          'password': self.password}

        delete_action = self.session.post(self.get_url('planetGiveup'), headers=headers, data=delete_payload).content


    def calc_consomation(self, page_string, building_string, lvl):
        """ Retourne la consommation du batiment du level lvl + 1 """
        energieLvl = constants.Formules[page_string][building_string]['consommation'][0] * lvl * (
                constants.Formules[page_string][building_string]['consommation'][1] ** lvl)
        energieNextLvl = constants.Formules[page_string][building_string]['consommation'][0] * (lvl + 1) * (
                constants.Formules[page_string][building_string]['consommation'][1] ** (lvl + 1))
        return math.floor(energieNextLvl - energieLvl)

    def calc_building_cost(self, building, lvl):
        """ Retourne le cout d'un building_string lvl + 1 """
        cost = {}
        cost['metal'] = int(math.floor(constants.Formules[building]['cout']['metal'][0] *
                                       constants.Formules[building]['cout']['metal'][1] ** (lvl - 1)))
        cost['crystal'] = int(math.floor(constants.Formules[building]['cout']['crystal'][0] *
                                         constants.Formules[building]['cout']['crystal'][1] ** (lvl - 1)))
        cost['deuterium'] = int(math.floor(constants.Formules[building]['cout']['deuterium'][0] *
                                           constants.Formules[building]['cout']['deuterium'][1] ** (lvl - 1)))
        return cost

    def calc_building_time(self, cost, robotics, nano, speed):
        costSum = cost['metal'] + cost['crystal']
        buildTime = (costSum) / (2500 * (1 + robotics
                                         * (2 ** nano) * speed))
        # buildCost = self.OGame.building_cost('Storage', 'metal_storage', building['metal_storage'] + 1)
        # Time hours = Metal + crystal /   (  2500 * ( 1+ robotics * 2^nano * serverspeed )
        return buildTime

    def calc_production(self, type, batiment, lvl):
        """ Retourne le cout d'un batiment lvl + 1 """
        production = 0
        production = (self.universe_speed * constants.Formules[type][batiment]['production'][0] * lvl *
                      (constants.Formules[type][batiment]['production'][1] ** lvl)) + \
                     self.universe_speed * constants.Formules[type][batiment]['production'][0]

        return production

    def calc_storage_size(self, lvl):
        capacity = -1
        capacity = 5000 * int(math.floor(2.5 * (math.e ** (lvl * 20 / 33))))
        return capacity

    def galaxy_infos(self, galaxy, system):
        html = self.html_galaxy_content(galaxy, system)['galaxy']
        soup = BeautifulSoup(html, 'lxml')
        rows = soup.findAll('tr', {'class': 'row'})
        res = []
        for row in rows:
            if 'empty_filter' not in row.get('class'):
                activity = None
                activity_div = row.findAll('div', {'class': 'activity'})
                if len(activity_div) > 0:
                    activity_raw = activity_div[0].text.strip()
                    if activity_raw != '':
                        activity = int(activity_raw)
                    else:
                        activity = 0
                tooltips = row.findAll('div', {'class': 'htmlTooltip'})
                planet_tooltip = tooltips[0]
                planet_name = planet_tooltip.find('h1').find('span').text
                planet_url = planet_tooltip.find('img').get('src')
                coords_raw = planet_tooltip.find('span', {'id': 'pos-planet'}).text
                coords = re.search(r'\[(\d+):(\d+):(\d+)\]', coords_raw)
                galaxy, system, position = coords.groups()
                planet_infos = {}
                planet_infos['activity'] = activity
                planet_infos['name'] = planet_name
                planet_infos['img'] = planet_url
                planet_infos['coordinate'] = {}
                planet_infos['coordinate']['galaxy'] = int(galaxy)
                planet_infos['coordinate']['system'] = int(system)
                planet_infos['coordinate']['position'] = int(position)
                player_id = 9999
                player_name = "_9999_"
                player_rank = 9999
                metal_debris = 0
                crystal_debris = 0
                recyclers_needed = 0
                for i in range(1, len(tooltips)):
                    player_tooltip = tooltips[i]
                    player_id_raw = player_tooltip.get('id')
                    if player_id_raw.startswith('player'):
                        player_id = int(re.search(r'player(\d+)', player_id_raw).groups()[0])
                        player_name = player_tooltip.find('h1').find('span').text
                        rank = player_tooltip.find('li', {'class': 'rank'})
                        if rank is None:
                            player_rank = 9999
                        else:
                            player_rank = parse_int(rank.find('a').text)
                    if player_id_raw.startswith('debris'):
                        txt = tooltips[i].text
                        metal_debris = int(re.search(r'Metal: ([\d\.]+)', txt).groups()[0].replace(".", ""))
                        crystal_debris = int(re.search(r'Crystal: ([\d\.]+)', txt).groups()[0].replace(".", ""))
                        recyclers_needed = int(re.search(r'Recyclers needed: ([\d\.]+)', txt).groups()[0].replace(".", ""))
                planet_infos['player'] = {}
                planet_infos['player']['id'] = player_id
                planet_infos['player']['name'] = player_name
                planet_infos['player']['rank'] = player_rank
                planet_infos["metal_debris"] = metal_debris
                planet_infos["crystal_debris"] = crystal_debris
                planet_infos["recyclers_needed"] = recyclers_needed
                res.append(planet_infos)
        return res

    def change_player_name(self, new_name):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        modal_content = self.session.get(self.get_url('changenick'), headers=headers).content
        payload = {'nick': new_name,
                   'pass': self.password,
                   'ajax': 1}
        self.session.post(self.get_url('changenick'), headers=headers, data=payload)

    def create_alliance(self, alliance_name, alliance_tag):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        url = self.get_url('allianceCreation', {'action': 16})
        payload = {'allyTag': alliance_tag,
                   'allyName': alliance_name,
                   'token': 'undefined'}
        html = self.session.post(url, headers=headers, data=payload).content
        soup = BeautifulSoup(html, 'lxml')
        a_name = soup.find('meta', {'name': 'ogame-alliance-name'})
        a_tag = soup.find('meta', {'name': 'ogame-alliance-tag'})

        alliance_data = {'alliance_name': '', 'alliance_tag': ''}

        if alliance_name is not None and alliance_tag is not None:
            alliance_data['alliance_name'] = alliance_name

        return alliance_data

    def accept_alliance_requests(self):
        payload = {'ajax': 1}
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        html = self.session.post(self.get_url('allianceApplications'), headers=headers, data=payload).content
        soup = BeautifulSoup(html, 'lxml')
        actions = soup.find_all('a', {'class': 'action', 'rel': '3'})
        for idx, action in enumerate(actions):
            rel = action.attrs['rel']
            if idx % 2 == 0:
                form_value = action.attrs['rev'][0]
                form = form_value.replace('form_', '')
                token = action.attrs['token']
                url = self.get_url('allianceApplications',
                                   {'action': 3, 'applicationId': form, 'token': token, 'text': ''})
                content = self.session.post(url, headers=headers)

        return []

    def get_player_metas(self):
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res, 'lxml')
        player_id = soup.find('meta', {'name': 'ogame-player-id'})['content']
        player_name = soup.find('meta', {'name': 'ogame-player-name'})['content']
        alliance_id = soup.find('meta', {'name': 'ogame-alliance-id'})['content']
        alliance_name = soup.find('meta', {'name': 'ogame-alliance-name'})['content']
        alliance_tag = soup.find('meta', {'name': 'ogame-alliance-tag'})['content']

        data = {'player_id': player_id, 'player_name': player_name, 'alliance_id': alliance_id,
                'alliance_tag': alliance_tag, 'alliance_name': alliance_name}

        return data

    def get_max_colonies(self):
        astro_level = self.get_research()['astrophysics']
        if astro_level % 2 == 1:
            astro_level = astro_level + 1

        return astro_level / 2

    def can_colonize_more_planets(self):
        planet_list = self.get_planet_ids()
        max_colonies = self.get_max_colonies()

        if len(planet_list) < max_colonies:
            return True
        else:
            return False

    def metal_mine_production(self, level, universe_speed=1):
        return int(math.floor(30 * level * 1.1 ** level) * universe_speed)

    def crystal_mine_production(self, level, universe_speed=1):
        return int(math.floor(20 * level * 1.1 ** level) * universe_speed)

    def deuterium_synthesizer_production(self, level, max_temperature, universe_speed=1):
        return int(math.floor(10 * level * 1.1 ** level) * (1.44 - 0.004 * max_temperature) * universe_speed)

    def SolarPlantProduction(self, level):
        return int(math.floor(20 * level * 1.1 ** level))

    def FusionReactorProduction(self, research_energietechnik, level, engineer=False):
        if engineer is True:
            return int(round(math.floor(30 * level * (1.05 + research_energietechnik * 0.01) ** level) * 1.1))
        return int(round(math.floor(30 * level * (1.05 + research_energietechnik * 0.01) ** level) * 1.0))

    def SolarSatelliteProduction(self, max_temperature, amount, engineer=False):
        if engineer is True:
            return int(math.floor((max_temperature + 140.0) / 6.0) * amount * 1.1)
        return int(math.floor((max_temperature + 140) / 6) * amount)

    def get_research_cost(self, research_id, targetLevel, currentLevel=-1):
        targetKosten = [0.0, 0.0, 0.0]

        metallkosten = 0.0
        kristallkosten = 0.0
        deuteriumkosten = 0.0

        if currentLevel == -1:
            currentLevel = targetLevel - 1

        if research_id == 113:
            metallkosten = 0.0
            kristallkosten = 800.0 * \
                (2 ** targetLevel) - 800.0 - \
                (800.0 * (2 ** currentLevel) - 800.0)
            deuteriumkosten = 400.0 * \
                (2 ** targetLevel) - 400.0 - \
                (400.0 * (2 ** currentLevel) - 400.0)
        elif research_id == 120:
            metallkosten = 200.0 * (2 ** targetLevel) - \
                200.0 - (200.0 * (2 ** currentLevel) - 200.0)
            kristallkosten = 100.0 * \
                (2 ** targetLevel) - 100.0 - \
                (100.0 * (2 ** currentLevel) - 100.0)
            deuteriumkosten = 0.0
        elif research_id == 121:
            metallkosten = 1000 * (2.0 ** targetLevel) - \
                1000 - (1000 * (2 ** currentLevel) - 1000)
            kristallkosten = 300 * (2.0 ** targetLevel) - \
                300 - (300 * (2 ** currentLevel) - 300)
            deuteriumkosten = 100 * (2.0 ** targetLevel) - \
                100 - (100 * (2 ** currentLevel) - 100)
        elif research_id == 122:
            metallkosten = 2000 * (2.0 ** targetLevel) - \
                2000 - (2000 * (2 ** currentLevel) - 2000)
            kristallkosten = 4000 * (2.0 ** targetLevel) - \
                4000 - (4000 * (2 ** currentLevel) - 4000)
            deuteriumkosten = 1000 * \
                (2.0 ** targetLevel) - 1000 - \
                (1000 * (2 ** currentLevel) - 1000)
        elif research_id == 114:
            metallkosten = 0.0
            kristallkosten = 4000 * (2.0 ** targetLevel) - \
                4000 - (4000 * (2 ** currentLevel) - 4000)
            deuteriumkosten = 2000 * \
                (2.0 ** targetLevel) - 2000 - \
                (2000 * (2 ** currentLevel) - 2000)
        elif research_id == 199:
            metallkosten = 0.0
            kristallkosten = 0.0
            deuteriumkosten = 0.0
        elif research_id == 106:
            metallkosten = 200 * (2.0 ** targetLevel) - \
                200 - (200 * (2 ** currentLevel) - 200)
            kristallkosten = 1000 * (2.0 ** targetLevel) - \
                1000 - (1000 * (2 ** currentLevel) - 1000)
            deuteriumkosten = 200 * (2.0 ** targetLevel) - \
                200 - (200 * (2 ** currentLevel) - 200)
        elif research_id == 108:
            metallkosten = 0.0
            kristallkosten = 400 * (2.0 ** targetLevel) - \
                400 - (400 * (2 ** currentLevel) - 400)
            deuteriumkosten = 600 * (2.0 ** targetLevel) - \
                600 - (600 * (2 ** currentLevel) - 600)
        elif research_id == 124:
            metallkosten = 16000.0 / 3 * ((1.75 ** targetLevel) - 1)
            kristallkosten = 32000.0 / 3 * ((1.75 ** targetLevel) - 1)
            deuteriumkosten = 16000.0 / 3 * ((1.75 ** targetLevel) - 1)
        elif research_id == 123:
            metallkosten = 240000 * (2.0 ** targetLevel) - \
                240000 - (240000 * (2 ** currentLevel) - 240000)
            kristallkosten = 400000 * \
                (2.0 ** targetLevel) - 400000 - \
                (400000 * (2 ** currentLevel) - 400000)
            deuteriumkosten = 160000 * \
                (2.0 ** targetLevel) - 160000 - \
                (160000 * (2 ** currentLevel) - 160000)
        elif research_id == 115:
            metallkosten = 400 * (2.0 ** targetLevel) - \
                400 - (400 * (2 ** currentLevel) - 400)
            kristallkosten = 0.0
            deuteriumkosten = 600 * (2.0 ** targetLevel) - \
                600 - (600 * (2 ** currentLevel) - 600)
        elif research_id == 117:
            metallkosten = 2000 * (2.0 ** targetLevel) - \
                2000 - (2000 * (2 ** currentLevel) - 2000)
            kristallkosten = 4000 * (2.0 ** targetLevel) - \
                4000 - (4000 * (2 ** currentLevel) - 4000)
            deuteriumkosten = 600 * (2.0 ** targetLevel) - \
                600 - (600 * (2 ** currentLevel) - 600)
        elif research_id == 118:
            metallkosten = 10000 * (2.0 ** targetLevel) - \
                10000 - (10000 * (2 ** currentLevel) - 10000)
            kristallkosten = 20000 * \
                (2.0 ** targetLevel) - 20000 - \
                (20000 * (2 ** currentLevel) - 20000)
            deuteriumkosten = 6000 * \
                (2.0 ** targetLevel) - 6000 - \
                (6000 * (2 ** currentLevel) - 6000)
        elif research_id == 109:
            metallkosten = 800 * (2.0 ** targetLevel) - \
                800 - (800 * (2 ** currentLevel) - 800)
            kristallkosten = 200 * (2.0 ** targetLevel) - \
                200 - (200 * (2 ** currentLevel) - 200)
            deuteriumkosten = 0.0
        elif research_id == 110:
            metallkosten = 200 * (2.0 ** targetLevel) - \
                200 - (200 * (2 ** currentLevel) - 200)
            kristallkosten = 600 * (2.0 ** targetLevel) - \
                600 - (600 * (2 ** currentLevel) - 600)
            deuteriumkosten = 0.0
        elif research_id == 111:
            metallkosten = 1000 * (2.0 ** targetLevel) - \
                1000 - (1000 * (2 ** currentLevel) - 1000)
            kristallkosten = 0.0
            deuteriumkosten = 0.0

        targetKosten[0] = metallkosten
        targetKosten[1] = kristallkosten
        targetKosten[2] = deuteriumkosten

        return targetKosten

    def rocketsilo_cost(self, level):
        metal = int(10000 * 2 ** level)
        crystal = int(10000 * 2 ** level)
        deuterium = int(500 * 2 ** level)
        return (metal, crystal, deuterium)

    def metal_mine_cost(self, level):
        metal = int(60 * 1.5 ** (level - 1))
        crystal = int(15 * 1.5 ** (level - 1))
        deuterium = int(0)
        return (metal, crystal, deuterium)

    def crystal_mine_cost(self, level):
        metal = int(48 * 1.6 ** (level - 1))
        crystal = int(24 * 1.6 ** (level - 1))
        deuterium = int(0)
        return (metal, crystal, deuterium)

    def deuterium_synthesizer_cost(self, level):
        metal = int(225 * 1.5 ** (level - 1))
        crystal = int(75 * 1.5 ** (level - 1))
        deuterium = int(0)
        return (metal, crystal, deuterium)

    def solar_plant_cost(self, level, existinglevel=0):
        metal = int(150 * ((1.5 ** level) - (1.5 ** existinglevel)))
        crystal = int(60 * ((1.5 ** level) - (1.5 ** existinglevel)))
        deuterium = int(0)
        return (metal, crystal, deuterium)

    def fusion_reactor_cost(self, level, existinglevel=0):
        metal = int(1125 * ((1.8 ** level) - (1.8 ** existinglevel)))
        crystal = int(450 * ((1.8 ** level) - (1.8 ** existinglevel)))
        deuterium = int(225 * ((1.8 ** level) - (1.8 ** existinglevel)))
        return (metal, crystal, deuterium)

    def building_production_time(metal, crystal, level_robotics_factory, level_nanite_factory, level, universe_speed=1):
        res = (metal + crystal) / (2500 * max(4 - level / 2, 1) * (1 +
                                                                   level_robotics_factory) * universe_speed * 2 ** level_nanite_factory) * 3600
        seconds = int(round(res))
        return seconds

    def building_production_time2(metal, crystal, level_robotics_factory, level_nanite_factory, level, universe_speed=1):
        """Nanite Factories, Lunar Bases, Sensor Phalanxes, and Jumpgates do not get the MAX() time reduction, so their formula is just"""
        res = (metal + crystal) / (2500 * (1 + level_robotics_factory)
                                   * universe_speed * 2 ** level_nanite_factory) * 3600
        seconds = int(round(res))
        return seconds

    def research_time(metal, crystal, research_lab_level):
        res = (metal + crystal) / (1000 * (1 + research_lab_level))
        seconds = int(round(res))
        return seconds

    def flightspeed_combustiondrive(self, shipbasespeed=0.0, level_combustion=1.0):
        # Grundgeschwindigkeit * (1 + (0, 1 * Stufe Verbrennungstriebwerk))
        return shipbasespeed * (1.0 + (0.1 * level_combustion))
