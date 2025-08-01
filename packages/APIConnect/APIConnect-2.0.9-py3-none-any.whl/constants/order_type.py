from enum import Enum, unique


@unique
class OrderTypeEnum(str, Enum) :
    '''
    Enum class for all the allowed types of Orders.
    '''
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP_LIMIT = 'STOP_LIMIT'
    STOP_MARKET = 'STOP_MARKET'