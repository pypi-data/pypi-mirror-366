import json
import logging
from typing import Any, Callable, List
from APIConnect.validator import Validator
from constants.streaming_constants import StreamingConstants
from feed.feed import Feed

LOGGER = logging.getLogger(__name__)


class ReducedQuotesFeed():

    @Validator.ValidateInputDataTypes
    def __init__(self, feedObj : Feed) -> None:
        self.__feed_obj = feedObj

    @Validator.isRequired(["symbols", "callBack"])
    def subscribeReducedQuotesFeed(self, symbols: List[str], callBack: Callable[[str], Any]) -> None:
        reducedQuote = self.__create_reduced_quote_request(symbols)
        LOGGER.debug("Subscribing Reduced quote feed with request: %s", reducedQuote)

        self.__feed_obj._subscribe(reducedQuote, callBack, StreamingConstants.REDUCED_QUOTE_SREAM_REQ_CODE)

    @Validator.isRequired(["symbols"])
    def unsubscribeReducedQuotesFeed(self) -> None:
        '''

         This method will unsubscribe from the streamer. After successful invokation, this will stop the streamer packets of the symbols subscribed.

        '''
        unsub_reduced_quote = self.__create_reduced_quote_request(subscribe = False)
        LOGGER.debug("Unsubscribing reduced quote feed with request: %s", unsub_reduced_quote)
        self.__feed_obj._unsubscribe(unsub_reduced_quote, StreamingConstants.REDUCED_QUOTE_SREAM_REQ_CODE)

    def __create_reduced_quote_request(self, symbols = [], subscribe: bool = True) -> str:

        symset = []
        for syms in symbols:
            symset.append({"symbol": syms})
        if subscribe:
            request_type = "subscribe"
        else:
            request_type = "unsubscribe"
        req = {
            "request":
                {
                    "streaming_type": "quote",
                    "data":
                        {
                            "accType": "EQ",
                            "symbols": symset
                        },
                    "formFactor": "P",
                    "appID": self.__feed_obj._appID,
                    "response_format": "json",
                    "request_type": request_type
                },
            "echo": {}
        }
        return json.dumps(req) + "\n"
