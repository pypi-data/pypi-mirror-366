from enum import Enum, unique


@unique
class ProductCodeENum(str, Enum) :
    '''
    Enum class for all the allowed types of Products.
    '''
    BO = 'BO'
    CO = 'CO'
    CNC = 'CNC'
    MIS = 'MIS'
    NRML = 'NRML'
    MTF = 'MTF'