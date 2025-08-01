import json
import logging
from typing import Any, Callable, List
from APIConnect.validator import Validator
from constants.streaming_constants import StreamingConstants
from feed.feed import Feed

LOGGER = logging.getLogger(__name__)


class MiniQuoteFeed():

    @Validator.ValidateInputDataTypes
    def __init__(self, feedObj : Feed) -> None:
        self.__feed_obj = feedObj

    @Validator.isRequired(["symbols", "callBack"])
    def subscribeMiniQuoteFeed(self, symbols: List[str], callBack: Callable[[str], Any]) -> None:
        miniQuote = self.__create_miniQuote_request(symbols)
        LOGGER.debug("Subscribing miniQuote feed with request: %s", miniQuote)

        self.__feed_obj._subscribe(miniQuote, callBack, StreamingConstants.MINI_QUOTE_STREAM_REQ_CODE)

    @Validator.isRequired(["symbols"])
    def unsubscribeMiniQuoteFeed(self) -> None:
        '''

         This method will unsubscribe from the streamer. After successful invokation, this will stop the streamer packets of the symbols subscribed.

        '''
        unsub_miniQuote = self.__create_miniQuote_request(subscribe = False)
        LOGGER.debug("Unsubscribing miniQuote feed with request: %s", unsub_miniQuote)
        self.__feed_obj._unsubscribe(unsub_miniQuote, StreamingConstants.MINI_QUOTE_STREAM_REQ_CODE)

    def __create_miniQuote_request(self, symbols = [], subscribe: bool = True) -> str:

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
                    "streaming_type": "miniquote",
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
