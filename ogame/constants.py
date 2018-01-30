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
    u'Metallmine': 1,
    u'Kristallmine': 2,
    u'Deuterium-Synthetisierer': 3,
    u'Solarkraftwerk': 4,
    u'Fusionskraftwerk': 12,
    u'Metallspeicher': 22,
    u'Kristallspeicher': 23,
    u'DeuteriumTank': 24
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
    u'Allianzdepot': 34,
    u'Roboterfabrik': 14,
    u'Raumschiffswerft': 21,
    u'Forschungslabor': 31,
    u'Raketensilo': 44,
    u'Nanitenfabrik': 15,
    u'Terraformer': 33,
    u'Raumdock': 36
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
    u'Raketenwerfer': 401,
    u'LeichterLaser': 402,
    u'SchwererLaser': 403,
    u'GaußKanone': 404,
    u'IonenKanone': 405,
    u'Plasmawerfer': 406,
    u'KleineSchildkuppel': 407,
    u'GroßeSchildkuppel': 408,
    u'Abfangrakete': 502,
    u'Interplanetarrakete': 503
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
    u'Kleiner Transporter': 202,
    u'Großer Transporter': 203,
    u'Leichter Jäger': 204,
    u'Schwerer Jäger': 205,
    u'Kreuzer': 206,
    u'Schlachtschiff': 207,
    u'Kolonieschiff': 208,
    u'Recycler': 209,
    u'Spionagesonde': 210,
    u'Bomber': 211,
    u'Solarsatellit': 212,
    u'Zerstörer': 213,
    u'Todesstern': 214,
    u'Schlachtkreuzer': 215
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
