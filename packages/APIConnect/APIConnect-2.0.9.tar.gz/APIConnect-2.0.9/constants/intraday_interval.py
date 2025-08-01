from enum import Enum, unique


@unique
class IntradayIntervalEnum(str, Enum) :
    '''
    Enum class for all the allowed types of Intraday Intervals.
    '''
    M1 = "M1"
    M3 = "M3"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"