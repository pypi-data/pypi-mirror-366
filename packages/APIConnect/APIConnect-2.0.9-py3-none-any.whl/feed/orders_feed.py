import json
import logging
from typing import Any, Callable
from APIConnect.validator import Validator
from constants.streaming_constants import StreamingConstants
from feed.feed import Feed

LOGGER = logging.getLogger(__name__)


class OrdersFeed():


    def __init__(self, feedObj : Feed, acc_id : str, user_id : str) -> None:
        self.acc_id = acc_id
        self.user_id = user_id
        self.__feed_obj = feedObj

    @Validator.isRequired(["callBack"])
    def subscribeOrdersFeed(self, callBack: Callable[[str], Any]) -> None:
        order_req = self.__create_order_request()
        LOGGER.debug(f"Subscribing orders feed with request: {order_req}")
        # self.__feed_obj._socket_fs.writelines(order_req)
        # self.__feed_obj._socket_fs.flush()

        self.__feed_obj._subscribe(order_req, callBack, StreamingConstants.ORDER_STREAM_REQ_CODE)

    def unsubscribeOrdersFeed(self) -> None:
        unsub_order_req = self.__create_order_request(subscribe=False)
        LOGGER.debug(
            f"Unsubscribing orders feed with request: {unsub_order_req}")
        self.__feed_obj._unsubscribe(unsub_order_req, StreamingConstants.ORDER_STREAM_REQ_CODE)

    def __create_order_request(self, subscribe: bool = True) -> str:

        if subscribe:
            req_type = "subscribe"
        else:
            req_type = "unsubscribe"

        req = {
            "request":
                {
                    "streaming_type": "orderFiler",
                    "data":
                        {
                            "accType": "EQ",
                            "userID": self.user_id,
                            "accID": self.acc_id,
                            "responseType": ["ORDER_UPDATE", "TRADE_UPDATE"]
                        },
                    "formFactor": "P",
                    "appID": self.__feed_obj._appID,
                    "response_format": "json",
                    "request_type": req_type,
                },
            "echo": {}
        }
        return json.dumps(req) + "\n"
