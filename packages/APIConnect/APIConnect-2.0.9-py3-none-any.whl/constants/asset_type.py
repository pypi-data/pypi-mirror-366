from enum import Enum, unique


@unique
class AssetTypeEnum(str, Enum) :
    '''
    Enum class for all the allowed types of Asset Types.
    '''
    INDEX = "INDEX"
    EQUITY = "EQUITY"
    OPTFUT = "OPTFUT"
    OPTCUR = "OPTCUR"
    OPTSTK = "OPTSTK"
    OPTIDX = "OPTIDX"
    FUTCOM = "FUTCOM"
    FUTCUR = "FUTCUR"
    FUTSTK = "FUTSTK"
    FUTIDX = "FUTIDX"