# coding: utf-8

Buildings = {'MetalMine': 1,
             'metal_mine': 1,
             'CrystalMine': 2,
             'crystal_mine': 2,
             'DeuteriumSynthesizer': 3,
             'deuterium_synthesizer': 3,
             'SolarPlant': 4,
             'solar_plant':4,
             'FusionReactor': 12,
             'MetalStorage': 22,
             'metal_storage': 22,
             'CrystalStorage': 23,
             'crystal_storage': 23,
             'DeuteriumTank': 24,
             'deuterium_tank': 24,
             'ShieldedMetalDen': 25,
             'UndergroundCrystalDen': 26,
             'SeabedDeuteriumDen': 27,


             'metal_mine': 1,
             'deuterium_synthesizer': 3,
             'solar_plant': 4,
             'solar_satellite': 212,
             'deuterium_tank': 24,
             'crystal_mine': 2,
             'fusion_reactor': 12,
             'metal_storage': 22,
             'crystal_storage': 23
             }

             'Minedemétal': 1,
             'Minedecristal': 2,
             'Synthétiseurdedeutérium': 3,
             'Centraleélectriquesolaire': 4,
             'Hangardemétal': 22,
             'Hangardecristal': 23,
             'Réservoirdedeutérium': 24}

Facilities = {'AllianceDepot': 34,
              'RoboticsFactory': 14,
              'Shipyard': 21,
              'shipyard': 21,
              'ResearchLab': 31,
              'research_lab': 31,
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

              # FR
              'Usinederobots': 14}


Defense = {'RocketLauncher': 401,
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


Ships = {'SmallCargo': 202,
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

         # FR
         'Grandtransporteur': 203,
         'Vaisseaudecolonisation': 208,
         'Satellitesolaire': 212}

Research = {'EspionageTechnology': 106,
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

            # FR
            'TechnologieOrdinateur': 108,
            'Astrophysique': 124,
            'TechnologieEspionnage': 106,
            'TechnologieBouclier': 111,
            'TechnologieProtectiondesvaisseauxspatiaux': 110}

Speed = {'10%': 1,
         '20%': 2,
         '30%': 3,
         '40%': 4,
         '50%': 5,
         '60%': 6,
         '70%': 7,
         '80%': 8,
         '90%': 9,
         '100%': 10}

Missions = {'Attack': 1,
            'GroupedAttack': 2,
            'Transport': 3,
            'Park': 4,
            'Deploy' : 4,
            'ParkInThatAlly': 5,
            'Spy': 6,
            'Colonize': 7,
            'RecycleDebrisField': 8,
            'Destroy': 9,

            'Expedition': 15,
            'DeployToMoon': 4,
            'DeployToPlanet': 4}
            'Expedition': 15}







Formules = {
        'batiments' : {
            'metal_mine': { 
                'cout': {
                    'Metal':[60,1.5], 'Crystal':[15,1.5], 'Deuterium':[0,0]
                },
                'production': [30,1.1],
                'consommation': [10,1.1],
            },
            'crystal_mine':{
                'cout': {
                    'Metal':[48, 1.6], 'Crystal':[24,1.6], 'Deuterium':[0,0]
                    },
                'production': [20,1.1],
                'consommation': [10,1.1],
            },
            'deuterium_synthesizer':{
                'cout': {
                    'Metal':[225,1.5], 'Crystal':[75,1.5], 'Deuterium':[0,0]
                    },
                'production': [10,1.1],
                'consommation': [20,1.1]
            },
        },
        'energy' : {
            'solar_plant':{
                'cout': {
                    'Metal':[75,1.5], 'Crystal':[30,1.5], 'Deuterium':[0,0]
                    },
                'production': [20,1.1],
                'consommation': [0,0]
            },
            'solar_satellite':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'production': [],
                'consommation': [0,0]
            },
            'fusion_reactor':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'production': [],
                'consommation': [10,1.1]
            },
        },
        'storage' :{
            'metal_storage':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'capacite': [1.6],
                'consommation': [0,0]
            },
            'crystal_storage':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'capacite': [1.6],
                'consommation': [0,0]
            },
            'deuterium_tank':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'capacite': [1.6],
                'consommation': [0,0]
            },
        }
    }


PlanetType = {'Planet': 1,
            'DebriField': 2,
            'Moon': 3


}
