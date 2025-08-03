
'''
    #This units list came from the UUC units list. https://github.com/Lemonexe/UUC/blob/master/app/data.js
    # it has been converted to python and contains all of the program constants, the unit database, and database of prefixes
    #In the python JSONGrapher repository, this is used (as of May 2025) simply to remove "plural" units.
    # In python JSONGrapher, the unitpy package is what is used for unit conversion.
    # 'en' is for English, 'cz' is for Czech, and "ae" is for American English.

    metre → meter
    mole → mol (sometimes abbreviated in scientific contexts)
    dioptre → diopter
    normal cubic metre → normal cubic meter
    normal litre → normal liter
    milimetre of mercury → millimeter of mercury
    litre → liter
    tonne → metric ton (often written as ton in American English)
    cubic centimetre → cubic centimeter

This file is adapted from UUC and is covered by the MIT License
        
MIT License

Copyright (c) 2017 Jiri Zbytovsky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


'''
import math as Math
#program constants
dict_csts = {
    "R": 8.3144598,  # [J/K/mol]
    "TC0": 273.15,  # [K]
    "TF0": 459.67 * 5 / 9,  # [K]
    "atm": 101325,  # [Pa]
    "mile": 1609.344,  # [m]
    "bbl": 158.987294928e-3,  # [m3]
    "q": 1.6021766208e-19,  # [C]
    "BTU": 1055.05585,  # [J]
    "APIk": 141.5e3,  # [1]
    "APIq": -131.5,  # [m3/kg]
    "dTnote": {"cz": "Viz °C pro důležitou poznámku.", "en": "See °C for an important note."},
    "Hgnote": {"cz": "Mezi mmHg a Torr je nepatrný rozdíl.", "en": "There is a negligible difference between mmHg and Torr."}
}

#Class to access the above dictionary objects with notation like javascript.
class Csts:
    def __init__(self, constants):
        self.__dict__.update(constants)

# Create an instance of Csts
csts = Csts(dict_csts)


'''
Units object is the database of all known units.
    v: [m,kg,s,A,K,mol,cd,$]      represents the vector of powers of basic units, for example N=kg*m/s^2, therefore v = [1,1,-2,0,0,0,0]
    id: string                    something unique. You can use the UnitConflicts() global function to detect possible id conflicts
    alias: array                  array of strings - other ids that reference the unitprefix:   
    name: object                  defines full name or even a short description for every language mutation
    k: number                     this coeficient equates value of the unit in basic units. For example minute = 60 seconds, therefore min.k = 60
    "SI": True/false                self-explanatory. This attribute doesn't really do anything, it's merely informational. Perhaps it's redundant, since all SI derived units have k = 1
    basic: True/false             whether it's basic SI unit or derived SI. Basic SI units are of utmost importance to the code, don't ever change them!
    prefix: all/+/-/undefined     it means: all prefixes allowed / only bigger than one allowed / lesser than one / prefixes disallowed. It's not really a restriction, just a recommendation.
    "constant": True/undefined      whether it is a constant. If true, attributes SI, basic and prefix are ignored. Prefix is disallowed.
    "note": a note that conveys anything important beyond description - what is noteworthy or weird about this unit or its usage. Implemented as an object of strings for all language mutations.
'''

units_dict_list = [
    # Eight basic units
    {"v": [1, 0, 0, 0, 0, 0, 0, 0], "id": "m", "name": {"cz": "metr", "en": "metre", "ae": "meter"}, "k": 1, "SI": True, "basic": True, "prefix": "all"},
    {"v": [0, 1, 0, 0, 0, 0, 0, 0], "id": "kg", "name": {"cz": "kilogram", "en": "kilogram"}, "k": 1, "SI": True, "basic": True, "note": {
        "cz": "To protože kilogram se obtížně programuje, neboť samo 'kilo' je předpona. Proto jsem definoval také gram jako odvozenou jednotku SI, která může mít jakékoliv předpony.",
        "en": "That's because kilogram is problematic to code, since the 'kilo' itself is a prefix. Therefore I have also defined gram as a derived SI unit, which can have all prefixes."
    }},
    {"v": [0, 0, 1, 0, 0, 0, 0, 0], "id": "s", "name": {"cz": "sekunda", "en": "second"}, "k": 1, "SI": True, "basic": True, "prefix": "-"},
    {"v": [0, 0, 0, 1, 0, 0, 0, 0], "id": "A", "name": {"cz": "ampér", "en": "ampere"}, "k": 1, "SI": True, "basic": True, "prefix": "all"},
    {"v": [0, 0, 0, 0, 1, 0, 0, 0], "id": "K", "name": {"cz": "kelvin", "en": "kelvin"}, "k": 1, "SI": True, "basic": True, "prefix": "all"},
    {"v": [0, 0, 0, 0, 0, 1, 0, 0], "id": "mol", "name": {"cz": "mol", "en": "mole"}, "k": 1, "SI": True, "basic": True, "prefix": "all"},
    {"v": [0, 0, 0, 0, 0, 0, 1, 0], "id": "cd", "name": {"cz": "kandela", "en": "candela"}, "k": 1, "SI": True, "basic": True, "prefix": "all"},
    # USD arbitrarily set as basic unit. Reference to this unit is hardcoded in currency loading!
    {"v": [0, 0, 0, 0, 0, 0, 0, 1], "id": "USD", "alias": ["$", "usd"], "name": {"cz": "americký dolar", "en": "US dollar"}, "k": 1, "basic": True, "prefix": "+"},


    #ALL OTHER UNITS as {id: 'identifier',v: [0,0,0,0,0,0,0], "name": {"cz": 'CZ', "en": 'EN'}, "k":1, "SI": True, "prefix": 'all'},
    #SI derived
    {"v": [0,0,0,0,0,0,0,0], "id": '%', "name": {"cz": 'procento', "en": 'percent'}, "k":1e-2},
    {"v": [0,0,0,0,0,0,0,0], "id": 'ppm', "name": {"cz": 'dílů na jeden milion', "en": 'parts per million'}, "k":1e-6},
    {"v": [0,0,0,0,0,0,0,0], "id": 'ppb', "name": {"cz": 'dílů na jednu miliardu', "en": 'parts per billion'}, "k":1e-9},
    {"v": [0,0,0,0,0,0,0,0], "id": 'rad', "name": {"cz": 'radián', "en": 'radian'}, "k":1, "SI": True, "prefix": '-', "note": {
        "cz": 'Úhel považuji za bezrozměrné číslo, čili radián je identický s číslem 1.',
        "en": 'I consider angle units to be dimensionless, with radian being identical to number 1.'}},
    {"v": [0,0,0,0,0,0,0,0], "id": '°', "alias":['deg'], "name": {"cz": 'stupeň', "en": 'degree'}, "k":Math.pi/180},
    {"v": [0,0,0,0,0,0,0,0], "id": 'gon', "name": {"cz": 'gradián', "en": 'gradian'}, "k":Math.pi/200},
    {"v": [0,0,-1,0,0,0,0,0], "id": 'Hz', "name": {"cz": 'hertz', "en": 'hertz'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [1,1,-2,0,0,0,0,0], "id": 'N', "name": {"cz": 'newton', "en": 'newton'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [-1,1,-2,0,0,0,0,0], "id": 'Pa', "name": {"cz": 'pascal', "en": 'pascal'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'J', "name": {"cz": 'joule', "en": 'joule'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [2,1,-3,0,0,0,0,0], "id": 'W', "name": {"cz": 'watt', "en": 'watt'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [0,0,1,1,0,0,0,0], "id": 'C', "name": {"cz": 'coulomb', "en": 'coulomb'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [2,1,-3,-1,0,0,0,0], "id": 'V', "name": {"cz": 'volt', "en": 'volt'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [-2,-1,4,2,0,0,0,0], "id": 'F', "name": {"cz": 'farad', "en": 'farad'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [2,1,-3,-2,0,0,0,0], "id": 'ohm', "name": {"cz": 'ohm', "en": 'ohm'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [-2,-1,3,2,0,0,0,0], "id": 'S', "name": {"cz": 'siemens', "en": 'siemens'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [2,1,-2,-1,0,0,0,0], "id": 'Wb', "name": {"cz": 'weber', "en": 'weber'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [0,1,-2,-1,0,0,0,0], "id": 'T', "name": {"cz": 'tesla', "en": 'tesla'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [2,1,-2,-2,0,0,0,0], "id": 'H', "name": {"cz": 'henry', "en": 'henry'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [0,0,0,0,1,0,0,0], "id": '°C', "name": {"cz": 'stupeň Celsia', "en": 'degree Celsius'}, "k":1, "SI": True, "note": {
        "cz": '°C je považován za jednotku rozdílu teploty (ΔT). Absolutní teplota (T) je zapsána pomocí složených závorek, např. {10°C}, viz tutoriál',
        "en": '°C is considered to be a unit of temperature difference (ΔT). Absolute temperature (T) is written using curly braces, e.g. {10°C}, see tutorial'}},

    {"v": [0,0,0,0,0,0,1,0], "id": 'lm', "name": {"cz": 'lumen', "en": 'lumen'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [-2,0,0,0,0,0,1,0], "id": 'lx', "name": {"cz": 'lux', "en": 'lux'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [0,0,-1,0,0,0,0,0], "id": 'Bq', "name": {"cz": 'becquerel', "en": 'becquerel'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [0,0,-1,0,0,0,0,0], "id": 'Rd', "name": {"cz": 'rutherford', "en": 'rutherford'}, "k":1e6, "SI": True, "prefix": 'all'},
    {"v": [2,0,-2,0,0,0,0,0], "id": 'Gy', "name": {"cz": 'gray', "en": 'gray'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [2,0,-2,0,0,0,0,0], "id": 'Sv', "name": {"cz": 'sievert', "en": 'sievert'}, "k":1, "SI": True, "prefix": 'all'},
    {"v": [-1,0,0,0,0,0,0,0], "id": 'dpt', "name": {"cz": 'dioptrie', "en": 'dioptre', "ae":'diopter'}, "k":1, "SI": True},



    #non-SI
    {"v": [0,0,0,0,0,1,0,0], "id": 'Nm3', "alias":['Ncm'], "name": {"cz": 'normální krychlový metr', "en": 'normal cubic metre'}, "k":csts.atm/csts.TC0/csts.R, "note": {
        "cz": 'Definován při 0°C a 1 atm. Navzdory názvu je Nm3 jednotkou látkového množství, nikoliv objemu.',
        "en": 'Defined at 0°C and 1 atm. Despite the name, Nm3 is actually amount of substance, not volume.'}},
    {"v": [0,0,0,0,0,1,0,0], "id": 'Ndm3', "alias":['Nl'], "name": {"cz": 'normální litr', "en": 'normal litre', 'ae':"normal liter"}, "k":csts.atm/csts.TC0/csts.R/1000, "note": {"cz": 'Viz Nm3 pro vysvětlení.', "en": 'See Nm3 for explanation.'}},
    {"v": [0,0,0,0,0,1,0,0], "id": 'SCF', "name": {"cz": 'normální krychlová stopa', "en": 'standard cubic foot'}, "k":0.028317*csts.atm/288.7/csts.R, "note": {"cz": 'Viz Nm3 pro vysvětlení.', "en": 'See Nm3 for explanation.'}},

    {"v": [0,0,1,0,0,0,0,0], "id": 'min', "name": {"cz": 'minuta', "en": 'minute'}, "k":60},
    {"v": [0,0,1,0,0,0,0,0], "id": 'h', "name": {"cz": 'hodina', "en": 'hour'}, "k":3600},
    {"v": [0,0,1,0,0,0,0,0], "id": 'd', "alias":['day'], "name": {"cz": 'den', "en": 'day'}, "k":3600*24},
    {"v": [0,0,1,0,0,0,0,0], "id": 'week', "name": {"cz": 'týden', "en": 'week'}, "k":3600*24*7},
    {"v": [0,0,1,0,0,0,0,0], "id": 'ftn', "name": {"cz": 'dva týdny', "en": 'fortnight'}, "k":1209600, "prefix": 'all'},
    {"v": [0,0,1,0,0,0,0,0], "id": 'month', "alias":['mth', 'měs'], "name": {"cz": 'průměrný měsíc', "en": 'average month'}, "k":3600*24*30.436875, "note": {
        "cz": 'Vypočten z gregoriánského roku.',
        "en": 'Calculated from gregorian year.'}},
    {"v": [0,0,1,0,0,0,0,0], "id": 'yr', "alias":['year'], "name": {"cz": 'gregoriánský rok', "en": 'gregorian year'}, "k":3600*24*365.2425, "note": {
        "cz": 'Pokud si nejste jisti, který rok použít, zvolte tento. Juliánský rok je zastaralý.',
        "en": 'If you are unsure which year to use, pick this one. Julian year is obsolete.'}},
    {"v": [0,0,1,0,0,0,0,0], "id": 'jyr', "name": {"cz": 'juliánský rok', "en": 'julian year'}, "k":3600*24*365.25},

    {"v": [0,0,-1,0,0,0,0,0], "id": 'rpm', "name": {"cz": 'otáčky za minutu', "en": 'revolutions per minute'}, "k":1/60},

    {"v": [0,0,0,0,1,0,0,0], "id": '°F', "name": {"cz": 'stupeň Fahrenheita', "en": 'degree Fahrenheit'}, "k":5/9, "note": csts.dTnote},
    {"v": [0,0,0,0,1,0,0,0], "id": '°Re', "alias":['°Ré', '°r'], "name": {"cz": 'stupeň Réaumura', "en": 'degree Réaumur'}, "k":1.25, "note": csts.dTnote},
    {"v": [0,0,0,0,1,0,0,0], "id": '°R', "name": {"cz": 'Rankine', "en": 'Rankine'}, "k":5/9, "note": csts.dTnote},

    {"v": [1,0,0,0,0,0,0,0], "id": 'Å', "name": {"cz": 'angstrom', "en": 'angstrom'}, "k":1e-10, "SI": True},
    {"v": [1,0,0,0,0,0,0,0], "id": 'th', "name": {"cz": 'thou', "en": 'thou'}, "k":2.54e-5},
    {"v": [1,0,0,0,0,0,0,0], "id": 'in', "name": {"cz": 'palec', "en": 'inch'}, "k":2.54e-2},
    {"v": [1,0,0,0,0,0,0,0], "id": 'ft', "name": {"cz": 'stopa', "en": 'foot'}, "k":0.3048, "prefix": '+'},
    {"v": [1,0,0,0,0,0,0,0], "id": 'yd', "name": {"cz": 'yard', "en": 'yard'}, "k":0.9144},
    {"v": [1,0,0,0,0,0,0,0], "id": 'fur', "name": {"cz": 'furlong', "en": 'furlong'}, "k":201.168, "prefix": 'all'},
    {"v": [1,0,0,0,0,0,0,0], "id": 'mi', "name": {"cz": 'míle', "en": 'mile'}, "k":csts.mile},
    {"v": [1,0,0,0,0,0,0,0], "id": 'nmi', "name": {"cz": 'námořní míle', "en": 'nautical mile'}, "k":1852},
    {"v": [1,0,0,0,0,0,0,0], "id": 'au', "name": {"cz": 'astronomická jednotka', "en": 'astronomical unit'}, "k":149597870700, "prefix": '+'},
    {"v": [1,0,0,0,0,0,0,0], "id": 'pc', "name": {"cz": 'parsek', "en": 'parsec'}, "k":3.08567758149137e16, "prefix": '+'},
    {"v": [1,0,0,0,0,0,0,0], "id": 'ly', "name": {"cz": 'světelný rok', "en": 'light-year'}, "k":9460730472580800, "prefix": '+'},

    {"v": [2,0,0,0,0,0,0,0], "id": 'a', "name": {"cz": 'ar', "en": 'ar'}, "k":100, "SI": True, "prefix": '+'},
    {"v": [2,0,0,0,0,0,0,0], "id": 'ac', "name": {"cz": 'akr', "en": 'acre'}, "k":4046.872},
    {"v": [2,0,0,0,0,0,0,0], "id": 'darcy', "name": {"cz": 'darcy', "en": 'darcy'}, "k": 9.869233e-13},

    {"v": [3,0,0,0,0,0,0,0], "id": 'l', "name": {"cz": 'litr', "en": 'litre', "ae":'liter'}, "k":1e-3, "SI": True, "prefix": 'all'},
    {"v": [3,0,0,0,0,0,0,0], "id": 'pt', "name": {"cz": 'pinta', "en": 'pint'}, "k":568.261e-6},
    {"v": [3,0,0,0,0,0,0,0], "id": 'gal', "name": {"cz": 'americký galon', "en": 'US gallon'}, "k":3.785412e-3},
    {"v": [3,0,0,0,0,0,0,0], "id": 'bsh', "name": {"cz": 'americký bušl', "en": 'US bushel'}, "k":35.2391e-3},
    {"v": [3,0,0,0,0,0,0,0], "id": 'ccm', "name": {"cz": 'kubický centimetr', "en": 'cubic centimetr', "ae": 'cubic centimeter'}, "k":1e-6},
    {"v": [3,0,0,0,0,0,0,0], "id": 'bbl', "name": {"cz": 'barel ropy', "en": 'oil barrel'}, "k":csts.bbl, "prefix": '+'},

    {"v": [3,0,-1,0,0,0,0,0], "id": 'BPD', "name": {"cz": 'barel ropy za den', "en": 'oil barrel per day'}, "k":csts.bbl/3600/24, "prefix": '+'},

    {"v": [0,1,0,0,0,0,0,0], "id": 'g', "name": {"cz": 'gram', "en": 'gram'}, "k":1e-3, "SI": True, "prefix": 'all'},
    {"v": [0,1,0,0,0,0,0,0], "id": 't', "name": {"cz": 'tuna', "en": 'tonne', "ae":'metric ton'}, "k":1000, "SI": True, "prefix": '+'},
    {"v": [0,1,0,0,0,0,0,0], "id": 'gr', "name": {"cz": 'grain', "en": 'grain'}, "k":64.79891e-6},
    {"v": [0,1,0,0,0,0,0,0], "id": 'oz', "name": {"cz": 'once', "en": 'ounce'}, "k":28.349523e-3},
    {"v": [0,1,0,0,0,0,0,0], "id": 'ozt', "name": {"cz": 'trojská unce', "en": 'troy ounce'}, "k":31.1034768e-3},
    {"v": [0,1,0,0,0,0,0,0], "id": 'ct', "name": {"cz": 'karát', "en": 'carat'}, "k":200e-6},
    {"v": [0,1,0,0,0,0,0,0], "id": 'lb', "alias":['lbs'], "name": {"cz": 'libra', "en": 'pound'}, "k":0.45359237},
    {"v": [0,1,0,0,0,0,0,0], "id": 'st', "name": {"cz": 'kámen', "en": 'stone'}, "k":6.35029318},
    {"v": [0,1,0,0,0,0,0,0], "id": 'slug', "name": {"cz": 'slug', "en": 'slug'}, "k":14.593903},
    {"v": [0,1,0,0,0,0,0,0], "id": 'fir', "name": {"cz": 'firkin', "en": 'firkin'}, "k":40.8233133, "prefix": 'all'},
    {"v": [0,1,0,0,0,0,0,0], "id": 'ts', "name": {"cz": 'krátká tuna', "en": 'short ton'}, "k":907.18474},
    {"v": [0,1,0,0,0,0,0,0], "id": 'tl', "name": {"cz": 'imperiální tuna', "en": 'long ton'}, "k":1016},
    {"v": [0,1,0,0,0,0,0,0], "id": 'u', "alias":['Da'], "name": {"cz": 'dalton (atomová hmotnostní konstanta)', "en": 'dalton (unified atomic mass unit)'}, "k":1.660539040e-27},

    {"v": [1,0,-1,0,0,0,0,0], "id": 'mph', "name": {"cz": 'míle za hodinu', "en": 'mile per hour'}, "k":csts.mile/3600},
    {"v": [1,0,-1,0,0,0,0,0], "id": 'kn', "name": {"cz": 'uzel', "en": 'knot'}, "k":1852/3600},

    {"v": [1,1,-2,0,0,0,0,0], "id": 'dyn', "name": {"cz": 'dyn', "en": 'dyne'}, "k":1e-5, "prefix": 'all'},

    {"v": [2,1,-2,0,0,0,0,0], "id": 'Wh', "name": {"cz": 'watthodina', "en": 'watt-hour'}, "k":3600, "prefix": 'all'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'eV', "name": {"cz": 'elektronvolt', "en": 'electronvolt'}, "k":csts.q, "prefix": 'all'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'erg', "name": {"cz": 'erg', "en": 'erg'}, "k":1e-7, "SI": True, "prefix": 'all'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'Btu', "alias":['BTU','btu'], "name": {"cz": 'britská tepelná jednotka', "en": 'british thermal unit'}, "k":csts.BTU, "prefix": 'all'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'Chu', "alias":['CHU','chu'], "name": {"cz": 'celsiova jednotka tepla', "en": 'celsius heat unit'}, "k": 1.899101e3, "prefix": 'all'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'thm', "name": {"cz": 'therm', "en": 'therm'}, "k":csts.BTU*1e5, "prefix": 'all'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'cal', "name": {"cz": 'kalorie', "en": 'calorie'}, "k":4.184, "prefix": 'all'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'TNT', "name": {"cz": 'ekvivalent tuny TNT', "en": 'ton of TNT equivalent'}, "k":4.184e9, "prefix": '+'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'BOE', "alias": ['BFOE'], "name": {"cz": 'ekvivalent barelu ropy', "en": 'barrel of oil equivalent'}, "k":5.8e6*csts.BTU, "prefix": '+'},
    {"v": [2,1,-2,0,0,0,0,0], "id": 'GGE', "name": {"cz": 'ekvivalent galonu benzínu', "en": 'gasoline gallon equivalent'}, "k":114e3*csts.BTU, "prefix": '+'},

    {"v": [-1,0,0,1,0,0,0,0], "id": 'Oe', "name": {"cz": 'oersted', "en": 'oersted'}, "k":1000/(4*Math.pi), "prefix": 'all'},

    {"v": [2,1,-3,0,0,0,0,0], "id": 'hp', "name": {"cz": 'imperiální koňská síla', "en": 'imperial horsepower'}, "k":745.69987158227022},

    {"v": [-1,1,-1,0,0,0,0,0], "id": 'P', "name": {"cz": 'poise', "en": 'poise'}, "k":0.1, "SI": True, "prefix": 'all'},
    {"v": [2,0,-1,0,0,0,0,0], "id": 'St', "name": {"cz": 'stokes', "en": 'stokes'}, "k":1e-4, "SI": True, "prefix": 'all'},

    {"v": [-1,1,-2,0,0,0,0,0], "id": 'bar', "name": {"cz": 'bar', "en": 'bar'}, "k":1e5, "SI": True, "prefix": 'all'},
    {"v": [-1,1,-2,0,0,0,0,0], "id": 'atm', "name": {"cz": 'atmosféra', "en": 'atmosphere'}, "k":csts.atm, "note": {
        "cz": 'Také slouží jako standardní tlak.',
        "en": 'Also serves as standard pressure.'}},
    {"v": [-1,1,-2,0,0,0,0,0], "id": 'mmHg', "name": {"cz": 'milimetr rtuťového sloupce', "en": 'millimetre of mercury', "ae": 'millimeter of mercury'}, "k":133.322387415, "note": csts.Hgnote},
    {"v": [-1,1,-2,0,0,0,0,0], "id": 'Torr', "alias":['torr'], "name": {"cz": 'torr', "en": 'torr'}, "k":csts.atm/760, "prefix": 'all', "note": csts.Hgnote},
    {"v": [-1,1,-2,0,0,0,0,0], "id": 'psi', "name": {"cz": 'libra na čtvereční palec', "en": 'pound per square inch'}, "k":6894.757293168362, "prefix": 'all'},

    {"v": [0,1,-2,-1,0,0,0,0], "id": 'G', "name": {"cz": 'gauss', "en": 'gauss'}, "k":0.0001, "SI": True, "prefix": 'all'},

    {"v": [0,0,-1,0,0,0,0,0], "id": 'Ci', "name": {"cz": 'Curie', "en": 'Curie'}, "k":3.7e10, "SI": False, "prefix": 'all'},
    {"v": [0,-1,1,1,0,0,0,0], "id": 'R', "name": {"cz": 'Rentgen', "en": 'Roentgen'}, "k":2.58e-4, "SI": False, "prefix": 'all'},
    {"v": [0,0,0,0,0,0,0,0], "id": 'monolayer',  "alias":['monolayers'], "name": {"cz": 'monolayer', "en": 'monolayer'}, "k":1},



    #constants
    {"v": [1,0,-2,0,0,0,0,0], "id": '_g', "name": {"cz": 'normální tíhové zrychlení', "en": 'standard gravity'}, "k":9.80665, "constant": True, "note": {
        "cz": 'Nikoliv univerzální konstanta, nýbrž konvenční.',
        "en": 'Not a universal constant, but a conventional one.'}},
    {"v": [1,0,-1,0,0,0,0,0], "id": '_c', "name": {"cz": 'rychlost světla ve vakuu', "en": 'speed of light in vacuum'}, "k":299792458, "constant": True},
    {"v": [3,-1,-2,0,0,0,0,0], "id": '_G', "name": {"cz": 'gravitační konstanta', "en": 'gravitational constant'}, "k":6.67408e-11, "constant": True},
    {"v": [2,1,-1,0,0,0,0,0], "id": '_h', "name": {"cz": 'Planckova konstanta', "en": 'Planck constant'}, "k":6.626070040e-34, "constant": True},
    {"v": [2,1,-2,0,-1,0,0,0], "id": '_k', "name": {"cz": 'Boltzmannova konstanta', "en": 'Boltzmann constant'}, "k":1.38064852e-23, "constant": True},
    {"v": [2,1,-2,0,-1,-1,0,0], "id": '_R', "name": {"cz": 'plynová konstanta', "en": 'gas constant'}, "k":csts.R, "constant": True},
    {"v": [1,1,-2,-2,0,0,0,0], "id": '_mu', "alias":['μ'], "name": {"cz": 'permeabilita vakua', "en": 'vacuum permeability'}, "k":1.2566370614e-6, "constant": True},
    {"v": [-3,-1,4,2,0,0,0,0], "id": '_E', "name": {"cz": 'permitivita vakua', "en": 'vacuum permittivity'}, "k":8.854187817e-12, "constant": True},
    {"v": [0,0,1,1,0,0,0,0], "id": '_q', "name": {"cz": 'elementární náboj', "en": 'elementary charge'}, "k":csts.q, "constant": True},
    {"v": [0,0,0,0,0,-1,0,0], "id": '_NA', "name": {"cz": 'Avogadrova konstanta', "en": 'Avogadro constant'}, "k":6.02214085e23, "constant": True},
    {"v": [0,0,0,0,0,0,0,0], "id": '_pi', "alias":['π'], "name": {"cz": 'Ludolfovo číslo', "en": 'Archimedes\' constant'}, "k":Math.pi, "constant": True},
    {"v": [0,0,0,0,0,0,0,0], "id": '_e', "name": {"cz": 'Eulerovo číslo', "en": 'Euler\'s number'}, "k":Math.e, "constant": True},
#     #special for Unitfuns, unusable without {}
#     {"v": [3,-1,0,0,0,0,0,0], "id": 'API', "alias":['°API'], "name": {"cz": 'API hustota', "en": 'API density'}, "k":1/141.5e3, onlyUnitfuns: True}, #theoretically, without {} API = specific volume unit
#     {"v": [0,0,0,0,0,0,0,0], "id": 'ln', "alias":['log'], "name": {"cz": 'Přirozený logaritmus', "en": 'Natural logarithm'}, "k":NaN, onlyUnitfuns: True}
];

# #unitfuns - irregular units that have a conversion function instead of mere ratio
# #{id: link to regular unit, f: function UF => SI, fi: inverse function SI => UF, "v": SI dimension (output when f, input when fi)}
# dict_Unitfuns = [
#     {id: '°C', f: UF => UF + csts.TC0, fi: SI => SI - csts.TC0, "v": [0,0,0,0,1,0,0,0]},
#     {id: '°F', f: UF => 5/9*UF + csts.TF0, fi: SI => 9/5*(SI - csts.TF0), "v": [0,0,0,0,1,0,0,0]},
#     {id: '°Re', f: UF => 1.25*UF + csts.TC0, fi: SI => 0.8*(SI - csts.TC0), "v": [0,0,0,0,1,0,0,0]},
#     {id: 'API', f: UF => csts.APIk/(UF - csts.APIq), fi: SI => csts.APIk/SI + csts.APIq, "v": [-3,1,0,0,0,0,0,0]},
#     {id: 'ln', f: UF => Math.log(UF), fi: SI => {throw '🏆 '+langService.trans('ERR_Secret');}, "v": [0,0,0,0,0,0,0,0]}
# ];

#currencies - their conversion ratio to dollar is unknown and will be obtained by currencies.php
#k and v will be filled later (v is always the same, k is obtained from API)
dict_Currencies = [
    {id: 'EUR', "alias":['€'], "name": {"cz": 'euro', "en": 'Euro'}},
    {id: 'AED', "name": {"cz": 'dirham Spojených arabských emirátů', "en": 'United Arab Emirates Dirham'}},
    {id: 'ARS', "name": {"cz": 'argentinské peso', "en": 'Argentine Peso'}},
    {id: 'AUD', "name": {"cz": 'australský dolar', "en": 'Australian Dollar'}},
    {id: 'BGN', "name": {"cz": 'bulharský lev', "en": 'Bulgarian Lev'}},
    {id: 'BRL', "name": {"cz": 'braziliský real', "en": 'Brazilian Real'}},
    {id: 'CAD', "name": {"cz": 'kanadský dolar', "en": 'Canadian Dollar'}},
    {id: 'CHF', "name": {"cz": 'švýcarský frank', "en": 'Swiss Franc'}},
    {id: 'CNY', "name": {"cz": 'čínský juan', "en": 'Chinese Yuan'}},
    {id: 'CZK', "alias":['Kč'], "name": {"cz": 'česká koruna', "en": 'Czech Republic Koruna'}},
    {id: 'DKK', "name": {"cz": 'dánská koruna', "en": 'Danish Krone'}},
    {id: 'GBP', "alias":['£'], "name": {"cz": 'britská libra', "en": 'British Pound Sterling'}},
    {id: 'HKD', "name": {"cz": 'hongkongský dolar', "en": 'Hong Kong Dollar'}},
    {id: 'HRK', "name": {"cz": 'chorvatská kuna', "en": 'Croatian Kuna'}},
    {id: 'HUF', "name": {"cz": 'maďarský forint', "en": 'Hungarian Forint'}},
    {id: 'IDR', "name": {"cz": 'indonéská rupie', "en": 'Indonesian Rupiah'}},
    {id: 'ILS', "name": {"cz": 'nový izraelský šekel', "en": 'Israeli New Sheqel'}},
    {id: 'INR', "name": {"cz": 'indická rupie', "en": 'Indian Rupee'}},
    {id: 'JPY', "alias": ['¥'], "name": {"cz": 'japonský jen', "en": 'Japanese Yen'}},
    {id: 'KRW', "name": {"cz": 'jihokorejský won', "en": 'South Korean Won'}},
    {id: 'MXN', "name": {"cz": 'mexické peso', "en": 'Mexican Peso'}},
    {id: 'NOK', "name": {"cz": 'norská koruna', "en": 'Norwegian Krone'}},
    {id: 'NZD', "name": {"cz": 'novozélandský dolar', "en": 'New Zealand Dollar'}},
    {id: 'PLN', "name": {"cz": 'polský zlotý', "en": 'Polish Zloty'}},
    {id: 'RON', "name": {"cz": 'rumunské leu', "en": 'Romanian Leu'}},
    {id: 'RUB', "name": {"cz": 'ruský rubl', "en": 'Russian Ruble'}},
    {id: 'SEK', "name": {"cz": 'švédská koruna', "en": 'Swedish Krona'}},
    {id: 'SGD', "name": {"cz": 'singapurský dolar', "en": 'Singapore Dollar'}},
    {id: 'THB', "name": {"cz": 'thajský baht', "en": 'Thai Baht'}},
    {id: 'TRY', "name": {"cz": 'turecká lira', "en": 'Turkish Lira'}},
    {id: 'VND', "name": {"cz": 'vietnamský dong', "en": 'Vietnamese Dong'}},
    {id: 'ZAR', "name": {"cz": 'jihoafrický rand', "en": 'South African Rand'}},
    {id: 'BTC', "name": {"cz": 'bitcoin', "en": 'Bitcoin'}}
];

#standard SI prefixes
dict_Prefixes = [
    {id: 'a', "v": -18},
    {id: 'f', "v": -15},
    {id: 'p', "v": -12},
    {id: 'n', "v": -9},
    {id: 'u', "v": -6},
    {id: 'μ', "v": -6},
    {id: 'm', "v": -3},
    {id: 'c', "v": -2},
    {id: 'd', "v": -1},
    {id: 'h', "v": 2},
    {id: 'k', "v": 3},
    {id: 'M', "v": 6},
    {id: 'G', "v": 9},
    {id: 'T', "v": 12},
    {id: 'P', "v": 15}
];

# Define the list of dictionaries
#Extract names in the specified order
def extract_names_by_order(units_dict_list, order):
    ordered_names = []
    for unit in units_dict_list:
        if "name" in unit:
            for key in order:
                if key in unit["name"]:
                    ordered_names.append(unit["name"][key])
    return ordered_names

def make_ids_dict(units_dict_list):
    ids_dict = {}
    for unit_dict in units_dict_list:
        if "id" in unit_dict:
            ids_dict[unit_dict["id"]] = unit_dict
    return ids_dict

# Specify the order of keys
name_order = ["ae", "en", "cz"]

#metric prefixes:
metric_prefixes = ["yotta", "zetta", "exa", "peta", "tera", "giga", "mega", "kilo", "hecto", "deca", "", "deci", "centi", "milli", "micro", "nano", "pico", "femto", "atto", "zepto", "yocto"]
metric_prefixes_greater = metric_prefixes[0:11] #first 10 
metric_prefixes_lesser = metric_prefixes[11:]
metric_prefixes_symbolic = ["Y", "Z", "E", "P", "T", "G", "M", "k", "h", "da", "", "d", "c", "m", "µ", "n", "p", "f", "a", "z", "y"]
metric_prefixes_symbolic_greater = metric_prefixes_symbolic[0:11] #first 10 
metric_prefixes_symbolic_lesser = metric_prefixes_symbolic[11:]

# Extract and print the names
ordered_name_list = extract_names_by_order(units_dict_list, name_order)
ids_dict = make_ids_dict(units_dict_list)

#now expand them with the metric prefix permutations
def expand_ids_list(ids_list, ids_dict):
    """
    Gives back the expanded names list by generating permutations with metric prefixes.
    Such as:
    ["km", "cm", "mm"]
    """
    expanded_ids_list = [] #now create the list to add to.
    for id in ids_list:
        if "prefix" in ids_dict[id]:
            if ids_dict[id]["prefix"] == "all":
                for metric_prefix_symbolic in metric_prefixes_symbolic:
                    expanded_ids_list.append(metric_prefix_symbolic+id)
            elif ids_dict[id]["prefix"] == "-":
                expanded_ids_list.append(id) #no prefix
                for metric_prefix_symbolic in metric_prefixes_symbolic_lesser:
                    expanded_ids_list.append(metric_prefix_symbolic+id)
            elif ids_dict[id]["prefix"] == "+":
                expanded_ids_list.append(id) #no prefix
                for metric_prefix_symbolic in metric_prefixes_symbolic_greater:
                    expanded_ids_list.append(metric_prefix_symbolic+id)
            else:
                expanded_ids_list.append(id) #no prefix
        else:
                expanded_ids_list.append(id) #no prefix
    return expanded_ids_list
ids_list = list(ids_dict.keys())
expanded_ids_list = expand_ids_list(ids_list, ids_dict)
expanded_ids_set = set(expanded_ids_list)

def expand_names_list(ids_list, ids_dict):
    """
    Gives back the expanded names list by generating permutations with metric prefixes.
    Such as:
    ["kilometer", "megameter", "gigameter"]
    
    The lines which say ids_dict[id]["alias"][0] could loop across aliases.
    However, there is usually only one alias, and the first is usually sufficient when there is more than one.
    """
    expanded_names_list = []  # Create the list to add to.
    for id in ids_list:
        if "prefix" in ids_dict[id]:
            if ids_dict[id]["prefix"] == "all": #for "all" prefix.
                #loop across prefixes, includes base case.
                for metric_prefix in metric_prefixes:  # Use "metric_prefixes".
                    expanded_names_list.append(metric_prefix + ids_dict[id]["name"]["en"])  # Use ids_dict[id]["name"]["en"] for concatenation.
                    if 'ae' in ids_dict[id]["name"]:
                        expanded_names_list.append(metric_prefix + ids_dict[id]["name"]["ae"]) 
                    if 'alias' in ids_dict[id]:
                        expanded_names_list.append(metric_prefix + ids_dict[id]["alias"][0])  
            elif ids_dict[id]["prefix"] == "-": #for "-" prefix.
                #base case
                expanded_names_list.append(ids_dict[id]["name"]["en"])  # No prefix.
                if 'ae' in ids_dict[id]["name"]:
                    expanded_names_list.append(ids_dict[id]["name"]["ae"])  # No prefix.
                if 'alias' in ids_dict[id]:
                    expanded_names_list.append(ids_dict[id]["alias"][0])  #No prefix.
                #loop across prefix cases
                for metric_prefix in metric_prefixes_lesser:  # Use lesser prefixes.
                    expanded_names_list.append(metric_prefix + ids_dict[id]["name"]["en"])
                    if 'ae' in ids_dict[id]["name"]:
                        expanded_names_list.append(metric_prefix + ids_dict[id]["name"]["ae"])
                    if 'alias' in ids_dict[id]:
                        expanded_names_list.append(metric_prefix + ids_dict[id]["alias"][0])
            elif ids_dict[id]["prefix"] == "+": #for "+" prefix.
                #base case
                expanded_names_list.append(ids_dict[id]["name"]["en"])  # No prefix.
                if 'ae' in ids_dict[id]["name"]:
                    expanded_names_list.append(ids_dict[id]["name"]["ae"])  # No prefix.
                if 'alias' in ids_dict[id]:
                    expanded_names_list.append(ids_dict[id]["alias"][0])
                #loop across prefixes
                for metric_prefix in metric_prefixes_greater:  # Use greater prefixes.
                    expanded_names_list.append(metric_prefix + ids_dict[id]["name"]["en"])
                    if 'ae' in ids_dict[id]["name"]:
                        expanded_names_list.append(metric_prefix + ids_dict[id]["name"]["ae"])
                    if 'alias' in ids_dict[id]:
                        expanded_names_list.append(metric_prefix + ids_dict[id]["alias"][0])
            else: #for odd prefix rules, we just use base case.
                #base case
                expanded_names_list.append(ids_dict[id]["name"]["en"])  # No prefix.
                if 'ae' in ids_dict[id]["name"]:
                    expanded_names_list.append(ids_dict[id]["name"]["ae"])  # No prefix.
                if 'alias' in ids_dict[id]:
                    expanded_names_list.append(ids_dict[id]["alias"][0])
        else: #for no prefix.
            expanded_names_list.append(ids_dict[id]["name"]["en"])  # No prefix.
            if 'ae' in ids_dict[id]["name"]:
                expanded_names_list.append(ids_dict[id]["name"]["ae"])  # No prefix.
            if 'alias' in ids_dict[id]:
                expanded_names_list.append(ids_dict[id]["alias"][0])
    return expanded_names_list


expanded_names_list = expand_names_list(ids_list, ids_dict)
expanded_names_set = set(expanded_names_list)


if __name__ == "__main__":
    #here is just the ordered name list.
    name_order = ["ae", "en", "cz"]
    ordered_name_list = extract_names_by_order(units_dict_list, name_order)
    print(ordered_name_list)
    #here is just the ordered name list for cz names.
    name_order = ["cz"]
    ordered_name_list = extract_names_by_order(units_dict_list, name_order)
    print(ordered_name_list)

    #here is just the ordered name list for en names.
    name_order = ["en"]
    ordered_name_list = extract_names_by_order(units_dict_list, name_order)
    print("\n", ordered_name_list)
    
    #print the ids_list:
    ids_list = make_ids_dict(units_dict_list)
    print(ids_list)
