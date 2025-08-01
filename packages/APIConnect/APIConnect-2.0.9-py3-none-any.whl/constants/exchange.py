from enum import Enum, unique


@unique
class ExchangeEnum(str, Enum) :
    '''
    Enum class for all the allowed types of Exchanges.
    '''
    NSE = 'NSE'
    BSE = 'BSE'
    NFO = 'NFO'
    CDS = 'CDS'
    MCX = 'MCX'
    NCDEX = 'NCDEX'
    BFO = 'BFO'