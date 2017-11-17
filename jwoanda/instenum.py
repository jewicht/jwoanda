
## generated using jwoanda.instruments.createInstrumentsEnum

from enum import Enum, unique

@unique
class Instruments(Enum):
    AU200_AUD = (0, "CFD", "Australia 200", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 2000.0, 0.02)
    AUD_CAD = (1, "CURRENCY", "AUD/CAD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    AUD_CHF = (2, "CURRENCY", "AUD/CHF", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    AUD_HKD = (3, "CURRENCY", "AUD/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    AUD_JPY = (4, "CURRENCY", "AUD/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    AUD_NZD = (5, "CURRENCY", "AUD/NZD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    AUD_SGD = (6, "CURRENCY", "AUD/SGD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    AUD_USD = (7, "CURRENCY", "AUD/USD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    BCO_USD = (8, "CFD", "Brent Crude Oil", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000.0, 0.02)
    CAD_CHF = (9, "CURRENCY", "CAD/CHF", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    CAD_HKD = (10, "CURRENCY", "CAD/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    CAD_JPY = (11, "CURRENCY", "CAD/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    CAD_SGD = (12, "CURRENCY", "CAD/SGD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    CHF_HKD = (13, "CURRENCY", "CHF/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    CHF_JPY = (14, "CURRENCY", "CHF/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    CHF_ZAR = (15, "CURRENCY", "CHF/ZAR", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    CN50_USD = (16, "CFD", "China A50", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 1000.0, 0.05)
    CORN_USD = (17, "CFD", "Corn", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 1500000.0, 0.033333)
    DE10YB_EUR = (18, "CFD", "Bund", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 60000.0, 0.02)
    DE30_EUR = (19, "CFD", "Germany 30", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 2500.0, 0.02)
    EU50_EUR = (20, "CFD", "Europe 50", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 3000.0, 0.02)
    EUR_AUD = (21, "CURRENCY", "EUR/AUD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_CAD = (22, "CURRENCY", "EUR/CAD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_CHF = (23, "CURRENCY", "EUR/CHF", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_CZK = (24, "CURRENCY", "EUR/CZK", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    EUR_DKK = (25, "CURRENCY", "EUR/DKK", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_GBP = (26, "CURRENCY", "EUR/GBP", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_HKD = (27, "CURRENCY", "EUR/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_HUF = (28, "CURRENCY", "EUR/HUF", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.05)
    EUR_JPY = (29, "CURRENCY", "EUR/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    EUR_NOK = (30, "CURRENCY", "EUR/NOK", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_NZD = (31, "CURRENCY", "EUR/NZD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_PLN = (32, "CURRENCY", "EUR/PLN", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    EUR_SEK = (33, "CURRENCY", "EUR/SEK", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_SGD = (34, "CURRENCY", "EUR/SGD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_TRY = (35, "CURRENCY", "EUR/TRY", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    EUR_USD = (36, "CURRENCY", "EUR/USD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    EUR_ZAR = (37, "CURRENCY", "EUR/ZAR", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    FR40_EUR = (38, "CFD", "France 40", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 2000.0, 0.02)
    GBP_AUD = (39, "CURRENCY", "GBP/AUD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    GBP_CAD = (40, "CURRENCY", "GBP/CAD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    GBP_CHF = (41, "CURRENCY", "GBP/CHF", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    GBP_HKD = (42, "CURRENCY", "GBP/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    GBP_JPY = (43, "CURRENCY", "GBP/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    GBP_NZD = (44, "CURRENCY", "GBP/NZD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    GBP_PLN = (45, "CURRENCY", "GBP/PLN", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    GBP_SGD = (46, "CURRENCY", "GBP/SGD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    GBP_USD = (47, "CURRENCY", "GBP/USD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    GBP_ZAR = (48, "CURRENCY", "GBP/ZAR", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    HK33_HKD = (49, "CFD", "Hong Kong 33", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 4000.0, 0.02)
    HKD_JPY = (50, "CURRENCY", "HKD/JPY", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    IN50_USD = (51, "CFD", "India 50", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 1000.0, 0.05)
    JP225_USD = (52, "CFD", "Japan 225", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 1000.0, 0.02)
    NAS100_USD = (53, "CFD", "US Nas 100", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 4000.0, 0.02)
    NATGAS_USD = (54, "CFD", "Natural Gas", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 2500000.0, 0.02)
    NL25_EUR = (55, "CFD", "Netherlands 25", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 20000.0, 0.02)
    NZD_CAD = (56, "CURRENCY", "NZD/CAD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    NZD_CHF = (57, "CURRENCY", "NZD/CHF", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    NZD_HKD = (58, "CURRENCY", "NZD/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    NZD_JPY = (59, "CURRENCY", "NZD/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    NZD_SGD = (60, "CURRENCY", "NZD/SGD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    NZD_USD = (61, "CURRENCY", "NZD/USD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    SG30_SGD = (62, "CFD", "Singapore 30", -1, 2, 0, 1.0, 1000.0, 0.5, 0.0, 3000.0, 0.02)
    SGD_CHF = (63, "CURRENCY", "SGD/CHF", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    SGD_HKD = (64, "CURRENCY", "SGD/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    SGD_JPY = (65, "CURRENCY", "SGD/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    SOYBN_USD = (66, "CFD", "Soybeans", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 600000.0, 0.033333)
    SPX500_USD = (67, "CFD", "US SPX 500", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 8000.0, 0.02)
    SUGAR_USD = (68, "CFD", "Sugar", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 40000000.0, 0.033333)
    TRY_JPY = (69, "CURRENCY", "TRY/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.05)
    TWIX_USD = (70, "CFD", "Taiwan Index", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 1000.0, 0.05)
    UK100_GBP = (71, "CFD", "UK 100", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 500.0, 0.02)
    UK10YB_GBP = (72, "CFD", "UK 10Y Gilt", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 60000.0, 0.02)
    US2000_USD = (73, "CFD", "US Russ 2000", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 10000.0, 0.02)
    US30_USD = (74, "CFD", "US Wall St 30", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 1000.0, 0.02)
    USB02Y_USD = (75, "CFD", "US 2Y T-Note", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 60000.0, 0.02)
    USB05Y_USD = (76, "CFD", "US 5Y T-Note", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 60000.0, 0.02)
    USB10Y_USD = (77, "CFD", "US 10Y T-Note", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 60000.0, 0.02)
    USB30Y_USD = (78, "CFD", "US T-Bond", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 60000.0, 0.02)
    USD_CAD = (79, "CURRENCY", "USD/CAD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    USD_CHF = (80, "CURRENCY", "USD/CHF", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    USD_CNH = (81, "CURRENCY", "USD/CNH", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    USD_CZK = (82, "CURRENCY", "USD/CZK", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    USD_DKK = (83, "CURRENCY", "USD/DKK", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    USD_HKD = (84, "CURRENCY", "USD/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    USD_HUF = (85, "CURRENCY", "USD/HUF", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.05)
    USD_INR = (86, "CURRENCY", "USD/INR", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.05)
    USD_JPY = (87, "CURRENCY", "USD/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    USD_MXN = (88, "CURRENCY", "USD/MXN", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    USD_NOK = (89, "CURRENCY", "USD/NOK", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    USD_PLN = (90, "CURRENCY", "USD/PLN", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    USD_SAR = (91, "CURRENCY", "USD/SAR", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    USD_SEK = (92, "CURRENCY", "USD/SEK", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    USD_SGD = (93, "CURRENCY", "USD/SGD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.02)
    USD_THB = (94, "CURRENCY", "USD/THB", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.05)
    USD_TRY = (95, "CURRENCY", "USD/TRY", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    USD_ZAR = (96, "CURRENCY", "USD/ZAR", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 100000000.0, 0.05)
    WHEAT_USD = (97, "CFD", "Wheat", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 1500000.0, 0.033333)
    WTICO_USD = (98, "CFD", "West Texas Oil", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000.0, 0.02)
    XAG_AUD = (99, "METAL", "Silver/AUD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.05)
    XAG_CAD = (100, "METAL", "Silver/CAD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.05)
    XAG_CHF = (101, "METAL", "Silver/CHF", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.05)
    XAG_EUR = (102, "METAL", "Silver/EUR", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.05)
    XAG_GBP = (103, "METAL", "Silver/GBP", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.05)
    XAG_HKD = (104, "METAL", "Silver/HKD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.05)
    XAG_JPY = (105, "METAL", "Silver/JPY", 0, 1, 0, 1.0, 10000.0, 5.0, 0.0, 1000000.0, 0.02)
    XAG_NZD = (106, "METAL", "Silver/NZD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.05)
    XAG_SGD = (107, "METAL", "Silver/SGD", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.05)
    XAG_USD = (108, "METAL", "Silver", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 1000000.0, 0.02)
    XAU_AUD = (109, "METAL", "Gold/AUD", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_CAD = (110, "METAL", "Gold/CAD", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_CHF = (111, "METAL", "Gold/CHF", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_EUR = (112, "METAL", "Gold/EUR", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_GBP = (113, "METAL", "Gold/GBP", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_HKD = (114, "METAL", "Gold/HKD", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_JPY = (115, "METAL", "Gold/JPY", 1, 0, 0, 1.0, 100000.0, 50.0, 0.0, 50000.0, 0.02)
    XAU_NZD = (116, "METAL", "Gold/NZD", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_SGD = (117, "METAL", "Gold/SGD", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_USD = (118, "METAL", "Gold", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.02)
    XAU_XAG = (119, "METAL", "Gold/Silver", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 50000.0, 0.05)
    XCU_USD = (120, "CFD", "Copper", -4, 5, 0, 1.0, 1.0, 0.0005, 0.0, 2500000.0, 0.05)
    XPD_USD = (121, "METAL", "Palladium", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 5000.0, 0.05)
    XPT_USD = (122, "METAL", "Platinum", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 5000.0, 0.05)
    ZAR_JPY = (123, "CURRENCY", "ZAR/JPY", -2, 3, 0, 1.0, 100.0, 0.05, 0.0, 100000000.0, 0.02)
    none = (124, "none", "none", 0, 0, 0, 0, 0, 0, 0, 0, 0.0)


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
    