#!/usr/bin/python
# -*- coding: utf-8 -*-

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

    # NL
    'Metaalmijn': 1,
    'Kristalmijn': 2,
    'Deuteriumfabriek': 3,
    'Zonne-energiecentrale': 4,
    'Fusiecentrale': 12,
    'Metaalopslag': 22,
    'Kristalopslag': 23,
    'Deuteriumtank': 24,

    # GER
    'Metallmine': 1,
    'Kristallmine': 2,
    'Deuteriumsynthetisierer': 3,
    'Solarkraftwerk': 4,
    'Fusionskraftwerk': 12,
    'Metallspeicher': 22,
    'Kristallspeicher': 23,
    'DeuteriumTank': 24
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

    # NL
    'Alliantiehanger': 34,
    'Robotfabriek': 14,
    'Werf': 21,
    'Onderzoekslab': 31,
    'Raketsilo': 44,
    'Nanorobotfabriek': 15,
    'Terravormer': 33,
    'Ruimtewerf': 36,

    # GER
    'Allianzdepot': 34,
    'Roboterfabrike': 14,
    'Schiffswerft': 21,
    'Forschungslabor': 31,
    'Raketensilo': 44,
    'Nanitenfabrik': 15,
    'Terraformer': 33,
    'Raumdock': 36
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
    'InterplanetaryMissiles': 503,

    # NL
    'Raketlanceerder': 401,
    'Kleinelaser': 402,
    'Grotelaser': 403,
    'Gausskannon': 404,
    'Ionkannon': 405,
    'Plasmakannon': 406,
    'Kleineplanetaireschildkoepel': 407,
    'GroteplanetaireschildkoepelLargeShieldDome': 408,
    'Antiballistischeraketten': 502,
    'Interplanetaireraketten': 503,

    # GER
    'Raketenwerfer': 401,
    'LeichterLaser': 402,
    'SchwererLaser': 403,
    u'GaußKanone': 404,
    'IonenKanone': 405,
    'Plasmawerfer': 406,
    'Kleine Schildkuppel': 407,
    'Große Schildkuppel': 408,
    'Abfangrakete': 502,
    'Interplanetarrakete': 503
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
    'Battlecruiser': 215,

    # NL
    'Kleinvrachtschip': 202,
    'Grootvrachtschip': 203,
    'Lichtgevechtsschip': 204,
    'Zwaargevechtsschip': 205,
    'Kruiser': 206,
    'Slagschip': 207,
    'Kolonisatiesschip': 208,
    'Recycler': 209,
    'Spionagesonde': 210,
    'Bommenwerper': 211,
    'Zonne-energiesatelliet': 212,
    'Vernietiger': 213,
    'Sterdesdoods': 214,
    'Interceptor': 215,

    # GER
    'Kleiner Transporter': 202,
    'Großer Transporter': 203,
    'Leichter Jäger': 204,
    'Schwerer Jäger': 205,
    'Kreuzer': 206,
    'Schlachtschiff': 207,
    'Kolonieschiff': 208,
    'Recycler': 209,
    'Spionagesonde': 210,
    'Bomber': 211,
    'Solarsatellit': 212,
    'Zerstörer': 213,
    'Todesstern': 214,
    'Schlachtkreuzer': 215
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

    # NL
    'Spionagetechniek': 106,
    'Computertechniek': 108,
    'Wapentechniek': 109,
    'Schildtechniek': 110,
    'Pantsertechniek': 111,
    'Energietechniek': 113,
    'Hyperruimtetechniek': 114,
    'Verbrandingsmotor': 115,
    'Impulsmotor': 117,
    'Hyperruimtemotor': 118,
    'Lasertechniek': 120,
    'Iontechniek': 121,
    'Plasmatechniek': 122,
    'IntergalactischOnderzoeksnetwerk': 123,
    'Astrofysica': 124,
    'Gravitontechniek': 199,

    # GER
    'Spionagetechnik': 106,
    'Computertechnik': 108,
    'Waffentechnik': 109,
    'Schildtechnik': 110,
    'Raumschiffpanzerung': 111,
    'Energietechnik': 113,
    'Hyperraumtechnik': 114,
    'Verbrennungstriebwerk': 115,
    'Impulstriebwerk': 117,
    'Hyperraumantrieb': 118,
    'Lasertechnik': 120,
    'Ionentechnik': 121,
    'Plasmatechnik': 122,
    'IntergalaktischesForschungsnetzwerk': 123,
    'Astrophysik': 124,
    'Gravitontechnik': 199
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
    'ParkInThatAlly': 5,
    'Spy': 6,
    'Colonize': 7,
    'RecycleDebrisField': 8,
    'Destroy': 9,
    'Expedition': 15
}
