# coding: utf-8

class construct:
    metal_mine = 1
    crystal_mine = 2
    deuterium_synthesizer = 3
    solar_plant = 4
    fusion_reactor = 12

    metal_storage = 22
    crystal_storage = 23
    deuterium_tank = 24

    alliance_depot = 34
    robotics_factory = 14
    shipyard = 21
    research_lab = 31
    missile_sil0 = 44
    nanite_factory = 15
    terraformer = 33
    space_doc = 3

    rocket_launcher = 401
    light_laser = 402
    heavy_laser = 403
    gauss_cannon = 404
    ion_cannon = 405
    plasma_tcurret = 406
    small_schield_dome = 407
    large_schield_dome = 408
    anti_ballistic_missiles = 502
    interplanetary_missiles =  503

    small_cargo = 202
    large_cargo = 203
    light_fighter = 204
    heavy_fighter = 205
    cruiser = 206
    battleship = 207
    colony_ship = 208
    recycler = 209
    espionage_probe = 210
    bomber = 211
    solar_satellite = 212
    destroyer = 213
    deathstar = 214
    battlecruiser = 215

    energy_technology = 113
    laser_technology = 120
    ion_technology = 121
    hyperspace_technology = 114
    plasma_technology = 122
    combustion_drive = 115
    impulse_drive = 117
    hyperspace_drive = 118
    espionage_technology = 106
    computer_technology = 108
    astrophysics = 124
    intergalactic_research_network = 123
    graviton_technology = 199
    weapons_technology = 109
    shielding_technology = 110
    armour_technology = 111

Buildings = {
    'MetalMine': 1,
    'CrystalMine': 2,
    'DeuteriumSynthesizer': 3,
    'SolarPlant': 4,
    'FusionReactor': 12,
    'MetalStorage': 22,
    'CrystalStorage': 23,
    'DeuteriumTank': 24,
    'ShieldedMetalDen': 25,
    'UndergroundCrystalDen': 26,
    'SeabedDeuteriumDen': 27,

    'metal_mine': 1,
    'deuterium_synthesizer': 3,
    'solar_plant': 4,
    'deuterium_tank': 24,
    'crystal_mine': 2,
    'fusion_reactor': 12,
    'metal_storage': 22,
    'crystal_storage': 23
}

Facilities = {
    'AllianceDepot': 34,
    'RoboticsFactory': 14,
    'Shipyard': 21,
    'ResearchLab': 31,
    'MissileSilo': 44,
    'NaniteFactory': 15,
    'Terraformer': 33,
    'SpaceDock': 36,

    'alliance_depot': 34,
    'robotics_factory': 14,
    'shipyard': 21,
    'research_lab': 31,
    'missile_silo': 44,
    'nanite_factory': 15,
    'terraformer': 33,
    'space_dock': 36
}

Defense = {
    'RocketLauncher': 401,
    'LightLaser': 402,
    'HeavyLaser': 403,
    'GaussCannon': 404,
    'IonCannon': 405,
    'PlasmaTurret': 406,
    'SmallShieldDome': 407,
    'LargeShieldDome': 408,
    'AntiBallisticMissiles': 502,
    'InterplanetaryMissiles': 503
}

Ships = {
    'SmallCargo': 202,
    'LargeCargo': 203,
    'LightFighter': 204,
    'HeavyFighter': 205,
    'Cruiser': 206,
    'Battleship': 207,
    'ColonyShip': 208,
    'Recycler': 209,
    'EspionageProbe': 210,
    'Bomber': 211,
    'SolarSatellite': 212,
    'Destroyer': 213,
    'Deathstar': 214,
    'Battlecruiser': 215
 }

Research = {
    'EspionageTechnology': 106,
    'ComputerTechnology': 108,
    'WeaponsTechnology': 109,
    'ShieldingTechnology': 110,
    'ArmourTechnology': 111,
    'EnergyTechnology': 113,
    'HyperspaceTechnology': 114,
    'CombustionDrive': 115,
    'ImpulseDrive': 117,
    'HyperspaceDrive': 118,
    'LaserTechnology': 120,
    'IonTechnology': 121,
    'PlasmaTechnology': 122,
    'IntergalacticResearchNetwork': 123,
    'Astrophysics': 124,
    'GravitonTechnology': 199,

    'energy_technology': 113,
    'laser_technology': 120,
    'ion_technology': 121,
    'hyperspace_technology': 114,
    'plasma_technology': 122,
    'combustion_drive': 115,
    'impulse_drive': 117,
    'hyperspace_drive': 118,
    'espionage_technology': 106,
    'computer_technology': 108,
    'astrophysics': 124,
    'intergalactic_research_network': 123,
    'graviton_technology': 199,
    'weapons_technology': 109,
    'shielding_technology': 110,
    'armour_technology': 111
}

Speed = {
    '10%': 1,
    '20%': 2,
    '30%': 3,
    '40%': 4,
    '50%': 5,
    '60%': 6,
    '70%': 7,
    '80%': 8,
    '90%': 9,
    '100%': 10
}

Missions = {
    'Attack': 1,
    'GroupedAttack': 2,
    'Transport': 3,
    'Park': 4,
    'Deploy': 4,
    'ParkInThatAlly': 5,
    'Spy': 6,
    'Colonize': 7,
    'RecycleDebrisField': 8,
    'Destroy': 9,

    'Expedition': 15,
    'DeployToMoon': 4,
    'DeployToPlanet': 4
}

Formules = {
    'nano_factory': {
        'cout': {
            'metal': [1000000, 2], 'crystal': [500000, 2], 'deuterium': [100000, 2]
        }
    },
    'metal_mine': {
        'cout': {
            'metal': [60, 1.5], 'crystal': [15, 1.5], 'deuterium': [0, 0]
        },
        'production': [30, 1.1],
        'consommation': [10, 1.1],
    },
    'crystal_mine': {
        'cout': {
            'metal': [48, 1.6], 'crystal': [24, 1.6], 'deuterium': [0, 0]
        },
        'production': [20, 1.1],
        'consommation': [10, 1.1],
    },
    'deuterium_synthesizer': {
        'cout': {
            'metal': [225, 1.5], 'crystal': [75, 1.5], 'deuterium': [0, 0]
        },
        'production': [10, 1.1],
        'consommation': [20, 1.1]
    },
    'solar_plant': {
        'cout': {
            'metal': [75, 1.5], 'crystal': [30, 1.5], 'deuterium': [0, 0]
        },
        'production': [20, 1.1],
        'consommation': [0, 0]
    },
    'solar_satellite': {
        'cout': {
            'metal': [0, 0], 'crystal': [0, 0], 'deuterium': [0, 0]
        },
        'production': [],
        'consommation': [0, 0]
    },
    'fusion_reactor': {
        'cout': {
            'metal': [0, 0], 'crystal': [0, 0], 'deuterium': [0, 0]
        },
        'production': [],
        'consommation': [10, 1.1]
    },
    # 5000*rounddown(2.5 * (e^(20* LEVLE /33))
    'metal_storage': {
        'cout': {
            'metal': [1000, 2], 'crystal': [0, 0], 'deuterium': [0, 0]
        },
        'capacite': [1.6],
        'consommation': [0, 0]
    },
    'crystal_storage': {
        'cout': {
            'metal': [500, 2], 'crystal': [250, 2], 'deuterium': [0, 0]
        },
        'capacite': [1.6],
        'consommation': [0, 0]
    },
    'deuterium_tank': {
        'cout': {
            'metal': [1000, 2], 'crystal': [1000, 2], 'deuterium': [0, 0]
        },
        'capacite': [1.6],
        'consommation': [0, 0]
    }
}

PlanetType = {
    'Planet': 1,
    'DebriField': 2,
    'Moon': 3
}