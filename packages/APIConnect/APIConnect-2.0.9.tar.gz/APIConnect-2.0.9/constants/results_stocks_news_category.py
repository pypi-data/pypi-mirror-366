from enum import Enum, unique

@unique
class ResultsAndStocksNewsCategoryEnum(str, Enum) :
    '''
    Enum class for Results and Stocks in News Live News Categories.
    '''
    Results = "Results"
    Stocks_in_News = "Stocks in News"