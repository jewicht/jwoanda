from enum import Enum, IntEnum, unique

@unique
class PositionStatus(IntEnum):
    OPENED = 1
    CLOSED = 2

@unique
class TradeDirection(Enum):
    SHORT = 0
    LONG = 1
    NEUTRAL = 2

@unique
class ExitReason(Enum):
    NORMAL = 0
    TP = 1
    SL = 2
    TS = 3
    END = 4
    LIFETIME = 5
    FLIP = 6
    NOREASON = 7

@unique
class Events(IntEnum):
    TICK = 1
    CANDLE = 2
    KILL = 3

@unique
class Granularity(IntEnum):
    S5 = 5
    S10 = 10
    S15 = 15
    S30 = 30
    M1 = 60
    M2 = 60*2
    M3 = 60*3
    M4 = 60*4
    M5 = 60*5
    M10 = 60*10
    M15 = 60*15
    M30 = 60*30
    H1 = 60*60
    H2 = 60*60*2
    H3 = 60*60*3
    H4 = 60*60*4
    H6 = 60*60*6
    H8 = 60*60*8
    H12 = 60*60*12

class VolumeGranularity(object):
    def __init__(self, value):
        self._volume = int(value)

    @property
    def volume(self):
        return self._volume

    @property
    def name(self):
        return 'VOL{}'.format(self._volume)
    
@unique
class Candle(IntEnum):
    openBid = 0
    openAsk = 1
    highBid = 2
    highAsk = 3
    lowBid = 4
    lowAsk = 5
    closeBid = 6 
    closeAsk = 7
    volume = 8
    time = 9
    complete = 10
