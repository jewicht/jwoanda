from __future__ import print_function

import v20

from jwoanda.oandaaccount import oandaenv

def inststring(cnt, instrument):
    return "{} = ({}, \"{}\", \"{}\", {}, {}, {}, {}, {}, {}, {}, {}, {})".format(
        instrument.name,
        cnt,
        instrument.type,
        instrument.displayName,
        instrument.pipLocation,
        instrument.displayPrecision,
        instrument.tradeUnitsPrecision,
        instrument.minimumTradeSize,
        instrument.maximumTrailingStopDistance,
        instrument.minimumTrailingStopDistance,
        instrument.maximumPositionSize,
        instrument.maximumOrderUnits,
        instrument.marginRate)


def createInstrumentsEnum():
    response = oandaenv.api().account.instruments(oandaenv.account_id)
    
    f = open('instenum.py', 'w')
    f.write("""
## generated using jwoanda.instruments.createInstrumentsEnum

from enum import Enum, unique

@unique
class Instruments(Enum):
""")
    

    instruments = response.get("instruments")
    instruments = sorted(instruments, key=lambda instrument: instrument.name)
    for cnt, instrument in enumerate(instruments):
        string = inststring(cnt, instrument)
        f.write("    {}\n".format(string))
        print(instrument)
        print("")
        
    f.write("""

    def __init__(self,
                 ID,
                 type,
                 displayName, 
                 pipLocation, 
                 displayPrecision, 
                 tradeUnitsPrecision, 
                 minimumTradeSize, 
                 maximumTrailingStopDistance,
                 minimumTrailingStopDistance,
                 maximumPositionSize,
                 maximumOrderUnits,
                 marginRate):
        self.ID = ID
        self.type = type
        self.displayName = displayName
        self.pipLocation = pipLocation
        self.displayPrecision = displayPrecision
        self.tradeUnitsPrecision = tradeUnitsPrecision
        self.minimumTradeSize = minimumTradeSize
        self.maximumTrailingStopDistance = maximumTrailingStopDistance
        self.minimumTrailingStopDistance = minimumTrailingStopDistance
        self.maximumPositionSize = maximumPositionSize
        self.maximumOrderUnits = maximumOrderUnits
        self.marginRate = marginRate
    

    @property
    def pip(self):
        return 10**(self.pipLocation)
    """)
    f.close()
