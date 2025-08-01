from enum import Enum, unique


@unique
class StreamingConstants(Enum) :
    '''
    Enum class for Streaming Request Codes.
    '''
    QUOTE_SREAM_REQ_CODE = 1
    ORDER_STREAM_REQ_CODE = 2
    LIVENEWS_STREAM_REQ_CODE = 3
    DEPTH_STREAM_REQ_CODE = 4
    MINI_QUOTE_STREAM_REQ_CODE = 5
    REDUCED_QUOTE_SREAM_REQ_CODE = 6