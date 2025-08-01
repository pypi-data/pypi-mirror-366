import json
import logging

LOGGER = logging.getLogger(__name__)

class WatchlistResource :
    def __init__(self, response : str) -> None:

        LOGGER.debug(f"{self.__class__.__name__} object is being created.")

        self._response = response
        self.__response_dict = json.loads(self._response)
        self.__messageID = self.__response_dict['msgID']
        self.__serverTime = self.__response_dict['srvTm']
        self.__data = self.__response_dict['data']

    def _getWatchlistFormatted(self) -> 'WatchlistResource' :
        LOGGER.debug("inside _getWatchlistFormatted method")

        formatted_resp_dict = {
                            'data' : self.__data,
                            'msgID' : self.__messageID,
                            'srvTm' : self.__serverTime
                            }
        self._response = json.dumps(formatted_resp_dict)
        return self