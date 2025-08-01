import logging
import json
from APIConnect.http import Http
from constants.router import Router

LOGGER = logging.getLogger(__name__)

class ReportService:
    def __init__(self, routerObj, httpObj) -> None:
        LOGGER.debug("ReportService object is being created.")

        self.__routerObj : Router = routerObj
        self.__http : Http = httpObj

    def _getAllTransactionHistory(self, accountCode, fromDate, toDate) -> str :
        LOGGER.debug("inside _getAllTransactionHistoryDetails method")

        url = self.__routerObj._TransactionHistoryURL().format(accountCode=accountCode, fromDate=fromDate, toDate=toDate)

        response = self.__getAllTransactionHistoryAPI(url, {})
        return response
    
    def __getAllTransactionHistoryAPI(self, url : str, queryParams) -> str:

        LOGGER.debug("inside __getAllTransactionHistoryAPI method")

        reply = self.__http._GetMethod(url, queryParams)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply