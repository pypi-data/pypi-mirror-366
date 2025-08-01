import json
import logging
from APIConnect.http import Http
from constants.router import Router
from resources.quote_resource import QuoteResource
from typing import List

LOGGER = logging.getLogger(__name__)

class QuoteService:
    def __init__(self, routerObj, httpObj) -> None:
        LOGGER.debug("QuoteService object is being created.")

        self.__routerObj : Router = routerObj
        self.__http : Http = httpObj

    def _getMarketDepth(self, symbol) -> str :
        LOGGER.debug("inside _getMarketDepth method")

        url = self.__routerObj._MarketDepthURL().format(symbol=symbol)

        # symbolList : List[str] = [symbol]
        # queryParams = {"sym" : symbol}

        response = self.__getMarketDepthAPI(url, {})
        if response :
            formatted_resp = QuoteResource(response)._getQuoteFormatted()._response
            return formatted_resp
        return response
    
    def __getMarketDepthAPI(self, url : str, queryParams) -> str:

        LOGGER.debug("inside __getMarketDepthAPI method")

        reply = self.__http._GetMethod(url, queryParams)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply