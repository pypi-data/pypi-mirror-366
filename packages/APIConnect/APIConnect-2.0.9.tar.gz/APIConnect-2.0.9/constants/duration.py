from enum import Enum, unique


@unique
class DurationEnum(str, Enum) :
    '''
    Enum class for all the allowed types of Durations.
    '''
    DAY = 'DAY'
    IOC = 'IOC'
    EOS = 'EOS'
    GTC = 'GTC'
    GTD = 'GTD'