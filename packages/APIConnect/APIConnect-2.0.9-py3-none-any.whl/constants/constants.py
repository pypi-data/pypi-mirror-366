from enum import Enum, unique


@unique
class BaseUrl(str, Enum) :
    '''
    Enum class for all the allowed types of Orders.
    '''
    BASE_EQ = "https://nc.nuvamawealth.com/edelmw-eq/eq/"
    BASE_COMM = "https://nc.nuvamawealth.com/edelmw-comm/comm/"
    BASE_CONTENT = "https://nc.nuvamawealth.com/edelmw-content/content/"
    BASE_LOGIN = "https://nc.nuvamawealth.com/edelmw-login/login/"
    # BASE_MF_LOGIN = "https://nc.nuvamawealth.com/edelmw-mf/mf/"
    BASE_REPORT = "https://nc.nuvamawealth.com/app-report/equity/"
    EQ_CONTRACT = "https://nc.nuvamawealth.com/app/toccontracts/instruments.zip"
    # MF_CONTRACT = "https://nc.nuvamawealth.com/app/toccontracts/mfInstruments.zip"