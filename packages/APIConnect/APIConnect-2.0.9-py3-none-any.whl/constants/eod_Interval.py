from enum import Enum, unique


@unique
class EODIntervalEnum(str, Enum) :
    '''
    Enum class for all the allowed types of EOD Intervals.
    '''
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"