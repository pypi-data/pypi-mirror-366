from enum import Enum, unique

@unique
class SegmentTypeEnum(str, Enum) :
    '''
    Enum class for all the allowed types of Segment.
    '''
    EQUITY = 'EQUITY'
    COMMODITY = 'COMMODITY'
