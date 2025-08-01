import json
import logging

LOGGER = logging.getLogger(__name__)

class LiveNewsResource :
    def __init__(self, response : str, group_type : str = None, category_dp_name : str = None) -> None:

        LOGGER.debug("LiveNewsResource object is being created.")

        self._response = response
        response_dict = json.loads(self._response)
        self.__messageID = response_dict['msgID']
        self.__serverTime = response_dict['srvTm']
        self.__data = response_dict['data']
        if group_type:
            self.group_type = group_type
        if category_dp_name:
            self.__category_dp_name = category_dp_name

    def _getCategoriesFormatted(self) -> 'LiveNewsResource' :
        '''Collect a list of all received categories'''

        LOGGER.debug("inside getNewsCategoriesFormatted method")

        categories = []
        for key, value in self.__data.items():
            if type(value) is list:
                for item in value:
                    if 'dpNm' in item.keys():
                        categories.append(item['dpNm'])


        formatted_response_dict = { 'data' : {"categories" : categories},
                                    'msgID' : self.__messageID,
                                    'srvTm' : self.__serverTime
                                    }

        self._response = json.dumps(formatted_response_dict)
        return self

    def _getNewsFormatted(self) -> 'LiveNewsResource' :
        LOGGER.debug("inside _getNewsFormatted method")

        if self.group_type == "NG" :
            response_type = "listResponse"
            news_list = self.__data[response_type]['content']

            newsItems = []
            for news_block in news_list :
                news_block.pop("guid", "KEY_NOT_FOUND")
                news_block.pop("timeText", "KEY_NOT_FOUND")
                newsItems.append(news_block)

            self.__data['content'] = newsItems


        elif self.group_type == "G" :
            response_type = "groupResponse"

            content = []
            for content_block in self.__data[response_type]['content'] :
                newsItems = []
                for news_block in content_block["newsItems"] :
                    news_block.pop("guid", "KEY_NOT_FOUND")
                    news_block.pop("timeText", "KEY_NOT_FOUND")
                    newsItems.append(news_block)
                content_block["newsItems"] = newsItems
                content.append(content_block)

            self.__data["content"] = content

        self.__data["first"] = self.__data[response_type]["first"]
        self.__data["last"] = self.__data[response_type]["last"]
        self.__data["number"] = self.__data[response_type]["number"]
        self.__data["size"] = self.__data[response_type]["size"]
        self.__data["totalElements"] = self.__data[response_type]["totalElements"]
        self.__data["totalPages"] = self.__data[response_type]["totalPages"]

        self.__data.pop("type", "KEY_NOT_FOUND")
        self.__data.pop(response_type, "KEY_NOT_FOUND")

        formatted_resp_dict = {
                            'data' : self.__data,
                            'msgID' : self.__messageID,
                            'srvTm' : self.__serverTime
                            }
        self._response = json.dumps(formatted_resp_dict)
        return self

    def _filterCategories(self, filter_categories : list, exclude : bool = True) -> 'LiveNewsResource' :
        '''
        If `exclude` is False, only the `categories` are exctracted from response.\n
        If `exclude` is True, categories other than the `categories` are extracted from response.
        '''
        LOGGER.debug("inside __filterCategories method")

        response_dict = json.loads(self._response)

        if exclude:
            filteredCategoriesList = list(set(response_dict['data']['categories']).difference(set(filter_categories)))
            response_dict['data']['categories'] = filteredCategoriesList
        else :
            news_list = []
            for news_block in response_dict['data']['content']:
                if news_block["category"] in filter_categories:
                    news_list.append(news_block)
            response_dict['data']['content'] = news_list

            if not news_list:
                response_dict['data']['msg'] = f"There are no news available for '{self.__category_dp_name if type(self.__category_dp_name) is str else ', '.join(self.__category_dp_name)}' on page {response_dict['data']['number']}. Please try in other pages."

        self._response = json.dumps(response_dict)
        return self