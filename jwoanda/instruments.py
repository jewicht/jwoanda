from __future__ import print_function

import v20

from jwoanda.oandaaccount import oandaenv

def createInstrumentsEnum():
    response = oandaenv.api().account.instruments(oandaenv.account_id)
    
    f = open('instenum.py', 'w')
    f.write("""
## generated using jwoanda.instruments.createInstrumentsEnum

from enum import Enum, unique

@unique
class Instruments(Enum):
""")
    

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
    
    instruments = response.get("instruments")
    instruments = sorted(instruments, key=lambda instrument: instrument.name)
    for cnt, instrument in enumerate(instruments):
        string = inststring(cnt, instrument)
        f.write("    {}\n".format(string))
        print(instrument)
        print("")

    instrument = v20.primitives.Instrument()
    instrument.name = 'none'
    instrument.type = 'none'
    instrument.displayName = 'none'
    instrument.pipLocation = 0
    instrument.displayPrecision = 0
    instrument.tradeUnitsPrecision = 0
    instrument.minimumTradeSize = 0
    instrument.maximumTrailingStopDistance = 0
    instrument.minimumTrailingStopDistance = 0
    instrument.maximumPositionSize = 0
    instrument.maximumOrderUnits = 0
    instrument.marginRate = 0.
    f.write("    {}\n".format(inststring(cnt + 1, instrument))) 
        
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
