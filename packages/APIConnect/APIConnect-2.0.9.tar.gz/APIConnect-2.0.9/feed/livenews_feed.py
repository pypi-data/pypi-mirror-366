import json
import logging
from typing import Any, Callable
from APIConnect.validator import Validator
from constants.streaming_constants import StreamingConstants
from feed.feed import Feed

LOGGER = logging.getLogger(__name__)


class LiveNewsFeed():

    def __init__(self, feedObj : Feed ) -> None:
        self.__feed_obj = feedObj

    @Validator.isRequired(["callBack"])
    def subscribeLiveNewsFeed(self, callBack: Callable[[str], Any]) -> None:
        livenews_req = self.__create_livenews_request()
        LOGGER.debug(f"Subscribing live news feed with request : {livenews_req}")

        self.__feed_obj._subscribe(livenews_req, callBack, StreamingConstants.LIVENEWS_STREAM_REQ_CODE)

    def unsubscribeLiveNewsFeed(self) -> None:
        unsub_news_req = self.__create_livenews_request(subscribe=False)
        LOGGER.debug(
            f"Unsubscribing live news feed with request : {unsub_news_req}")
        self.__feed_obj._unsubscribe(unsub_news_req, StreamingConstants.LIVENEWS_STREAM_REQ_CODE)

    def __create_livenews_request(self, subscribe: bool = True) -> str:

        if subscribe:
            req_type = "subscribe"
        else:
            req_type = "unsubscribe"

        req = {
            "request":
                {
                    "streaming_type": "news",
                    "formFactor": "P",
                    "appID": self.__feed_obj._appID,
                    "response_format": "json",
                    "request_type": req_type,
                },
            "echo": {}
        }
        return json.dumps(req) + "\n"
