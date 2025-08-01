import json
import logging
from typing import Any, Callable, List
from APIConnect.validator import Validator
from APIConnect.api_constants import ApiConstants
from constants.streaming_constants import StreamingConstants
from feed.feed import Feed

LOGGER = logging.getLogger(__name__)


class DepthFeed():

    @Validator.ValidateInputDataTypes
    def __init__(self, feedObj : Feed, constantsObj) -> None:
        self.__feed_obj = feedObj
        self.__constants : ApiConstants = constantsObj

    @Validator.isRequired(["symbols", "callBack"])
    def subscribeDepthFeed(self, symbols: List[str], callBack: Callable[[str], Any]) -> None:
        depth = self.__create_depth_request(symbols)
        LOGGER.debug("Subscribing depth feed with request: %s", depth)
        if "account_type_exception" in depth:
            return
        self.__feed_obj._subscribe(depth, callBack, StreamingConstants.DEPTH_STREAM_REQ_CODE)

    @Validator.isRequired(["symbols"])
    def unsubscribeDepthFeed(self) -> None:
        '''

         This method will unsubscribe from the streamer. After successful invokation, this will stop the streamer packets of the symbols subscribed.

        '''
        unsub_depth = self.__create_depth_request(subscribe = False)
        LOGGER.debug("Unsubscribing depth feed with request: %s", unsub_depth)
        self.__feed_obj._unsubscribe(unsub_depth, StreamingConstants.DEPTH_STREAM_REQ_CODE)

    def __create_depth_request(self, symbols = [], subscribe: bool = True) -> str:

        symset = []
        for syms in symbols:
            if ("_MCX" in syms.upper() or "_NCDEX" in syms.upper()) and self.__constants.Data['data']['lgnData']['accTyp'] == 'EQ':
                err = {"account_type_exception": "Symbol subscription error"}
                LOGGER.info(json.dumps(err))
                return json.dumps(err) + "\n"
            symset.append({"symbol": syms})
        if subscribe:
            request_type = "subscribe"
        else:
            request_type = "unsubscribe"
        req = {
            "request":
                {
                    "streaming_type": "quote2",
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
