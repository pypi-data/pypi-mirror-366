import logging
from constants.constants import BaseUrl
import urllib

class Router:

    def __init__(self, config_obj=None):

        self.LOGGER = logging.getLogger(__name__)
        self.LOGGER.info("Router object is being created.")

        self.baseurleq = BaseUrl.BASE_EQ.value
        self.baseurlcomm = BaseUrl.BASE_COMM.value
        self.baseurlcontent = BaseUrl.BASE_CONTENT.value
        self.baseurllogin = BaseUrl.BASE_LOGIN.value
        # self.basemflogin = BaseUrl.BASE_MF_LOGIN.value
        self.baseurlreport = BaseUrl.BASE_REPORT.value
        self.EquityContractURL = BaseUrl.EQ_CONTRACT.value
        # self.MFContractURL = BaseUrl.MF_CONTRACT.value

        if config_obj and 'GLOBAL' in config_obj:
            if config_obj['GLOBAL'].get('BasePathLogin'):
                self.baseurllogin = config_obj['GLOBAL']['BasePathLogin']
            if config_obj['GLOBAL'].get('BasePathEq'):
                self.baseurleq = config_obj['GLOBAL']['BasePathEq']
            if config_obj['GLOBAL'].get('BasePathComm'):
                self.baseurlcomm = config_obj['GLOBAL']['BasePathComm']
            # if config_obj['GLOBAL'].get('BasePathMf'):
            #     self.basemflogin = config_obj['GLOBAL']['BasePathMf']
            if config_obj['GLOBAL'].get('BasePathContent'):
                self.baseurlcontent = config_obj['GLOBAL']['BasePathContent']
            if config_obj['GLOBAL'].get('BasePathReport'):
                self.baseurlreport = config_obj['GLOBAL']['BasePathReport']
            if config_obj['GLOBAL'].get('EquityContractURL'):
                self.EquityContractURL = config_obj['GLOBAL']['EquityContractURL']
            # if config_obj['GLOBAL'].get('MFContractURL'):
            #     self.MFContractURL = config_obj['GLOBAL']['MFContractURL']
            if config_obj['GLOBAL'].get('AppIdKey'):
                self._AppIdKey = config_obj['GLOBAL']['AppIdKey']
            self.LOGGER.info("URL constants loaded with provided configuration file.")

    def _CheckUpdateURl(self):
        return urllib.parse.urljoin(self.baseurlcontent, "adhoc/lib/version/")

    def _OrderBookURL(self):
        return urllib.parse.urljoin(self.baseurleq, "order/book/{userid}/v1/")

    def _OrderBookURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "orderbook/{userid}?rTyp={reqtype}/")

    def _TradeBookURL(self):
        return urllib.parse.urljoin(self.baseurleq, "tradebook/v1/{userid}/")

    def _TradeBookURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "tradebook/{userid}/")

    def _NetPositionURL(self):
        return urllib.parse.urljoin(self.baseurleq, "positions/net/{userid}/")

    def _NetPositionURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "positions/{userid}/")

    def _PlaceTradeURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/placetrade/v1/{userid}/")

    def _PlaceTradeURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "trade/placetrade/{userid}/")

    def _PlaceBracketTradeURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/placebrackettrade/{userid}/")

    def _PlaceBasketTradeURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/basketorder/{userid}/")

    def _ExitBracketTradeURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/exitbrackettrade/{userid}/")

    def _PlaceGtcGtdTradeURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/placegtcgtdtrade/{userid}/")

    def _PlaceGtcGtdTradeURL_comm(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/placegtcgtdtrade/{userid}/")

    def _OrderDetailsURL(self):
        return urllib.parse.urljoin(self.baseurleq, "order/details/{userid}?nOID={orderid}")

    def _OrderDetailsURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "orderdetails/{userid}?oID={orderid}")

    def _OrderHistoryURL(self):
        return urllib.parse.urljoin(self.baseurleq, "order/history/{userid}?sDt={StartDate}&eDt={EndDate}/")

    def _OrderHistoryURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "orderhistory/{userid}?sDt={StartDate}&eDt={EndDate}/")

    def _ModifyTradeURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/modifytrade/v1/{userid}/")

    def _ModifyTradeURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "trade/modifytrade/{userid}/")

    def _CancelTradeURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/canceltrade/v1/{userid}/")

    def _CancelTradeURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "trade/canceltrade/v1/{userid}/")

    def _HoldingURL(self):
        return urllib.parse.urljoin(self.baseurleq, "holdings/v1/rmsholdings/{userid}/")

    def _HoldingURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "reports/detail/{userid}/")

    def _LimitsURL(self):
        return urllib.parse.urljoin(self.baseurleq, "limits/rmssublimits/{userid}/")

    def _LimitsURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "limits/{userid}/")

    def _GetAMOFlag(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/amoflag/")

    def _GetAMOFlag_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "trade/amostatus/{exch}")

    def _PositionSqOffURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/position/sqroff/{userid}/")
    
    def _PositionSqOffV1URL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/position/sqroff/v1/{userid}/")

    def _ConvertPositionURL(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/convertposition/v1/{userid}/")

    def _ConvertPositionURL_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "trade/positionconversion/{userid}/")

    def _PlaceAMOTrade(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/amo/placetrade/v1/{userid}/")

    def _PlaceAMOTrade_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "trade/amo/placetrade/{userid}/")

    def _ModifyAMOTrade(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/amo/modifytrade/v1/{userid}/")

    def _ModifyAMOTrade_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "trade/amo/modifytrade/{userid}/")

    def _CancelAMOTrade(self):
        return urllib.parse.urljoin(self.baseurleq, "trade/amo/canceltrade/v1/{userid}/")

    def _CancelAMOTrade_comm(self):
        return urllib.parse.urljoin(self.baseurlcomm, "trade/amo/canceltrade/v1/{userid}/")

    # MF Related APIs

    # def _PlaceMFURL(self):
    #     return urllib.parse.urljoin(self.basemflogin, "trade/{userid}/")

    # def _ModifyMFURL(self):
    #     return urllib.parse.urljoin(self.basemflogin, "trade/{userid}/")

    # def _CancelMFURL(self):
    #     return urllib.parse.urljoin(self.basemflogin, "trade/{userid}/")

    # def _HoldingsMFURL(self):
    #     return urllib.parse.urljoin(self.basemflogin, "holding/{userid}/")

    # def _OrderBookMFURL(self):
    #     return urllib.parse.urljoin(self.basemflogin, "order/{userid}?frDt={fromDate}&toDt={toDate}/")

    # Charts Related APIs

    def _ChartsURL(self):
        return urllib.parse.urljoin(self.baseurlcontent, "charts/v2/main/{interval}/{exc}/{aTyp}/{symbol}")

    # Live News related APIs

    def _LiveNewsCategoriesURL(self) -> str:
        return urllib.parse.urljoin(self.baseurlcontent, "liveNews/getfiltersandcatagories")

    def _GeneralNewsURL(self) -> str:
        return urllib.parse.urljoin(self.baseurlcontent, "liveNews/general")

    def _HoldingsNewsURL(self) -> str :
        return urllib.parse.urljoin(self.baseurleq, "news/eqholdings")

    def _LatestCorpActionsURL(self) -> str :
        return urllib.parse.urljoin(self.baseurlcontent, "events/latestcorpactions/{symbol}")

    # Watchlist related APIs

    def _WatchlistBaseGroupsURL(self):
        return urllib.parse.urljoin(self.baseurlcontent, "accounts/groups")

    def _WatchlistGetScripsURL(self):
        return urllib.parse.urljoin(self.baseurlcontent, "accounts/groups/symbols")

    def _WatchlistGroupNameURL(self):
        return urllib.parse.urljoin(self.baseurlcontent, "accounts/groups/{groupName}/")

    # Login related APIs

    def _LoginURL(self):
        return urllib.parse.urljoin(self.baseurllogin, "accounts/loginvendor/{vendorId}/")

    def _TokenURL(self):
        return urllib.parse.urljoin(self.baseurllogin, "accounts/logindata/")

    def _LogoutURL(self):
        return urllib.parse.urljoin(self.baseurllogin, "account/logoff/{userid}/")

    #SnapQuote related APIs

    def _MarketDepthURL(self):
        return urllib.parse.urljoin(self.baseurlcontent, "quote/scrip/{symbol}/")
    
    #Report related APIs

    def _TransactionHistoryURL(self):
        return urllib.parse.urljoin(self.baseurlreport, "pnl/transaction?accountId={accountCode}&fromDate={fromDate}&toDate={toDate}")
    