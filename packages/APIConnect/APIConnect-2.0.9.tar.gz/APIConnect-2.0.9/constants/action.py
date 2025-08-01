from enum import Enum, unique


@unique
class ActionEnum(str, Enum) :
    '''
    Enum class for all the allowed types of Actions.
    '''
    BUY = 'BUY'
    SELL = 'SELL'
