import json
import logging
from typing import Tuple, Union
from APIConnect.http import Http
from APIConnect.validator import Validator
from constants.results_stocks_news_category import ResultsAndStocksNewsCategoryEnum
from constants.router import Router
from exceptions.api_exception import APIError
from exceptions.validation_exception import ValidationException
from resources.live_news_resource import LiveNewsResource

LOGGER = logging.getLogger(__name__)

class LiveNewsService():
    def __init__(self, routerObj, httpObj, fileName) -> None:
        LOGGER.debug("LiveNewsService object is being created.")

        self.__routerObj : Router = routerObj
        self.__http : Http = httpObj
        self.__fileName = fileName
        self.__excludeCategories = ['Results', 'Stocks in News', 'My Holdings']
        self.__allCategoriesDataDict = {}
        self.__validCategoriesList = []

    def _getNewsCategories(self) -> str :
        LOGGER.debug("inside _getNewsCategories method")
        all_categories_resp = self.__getAllNewsCategories()
        if all_categories_resp != "":
            filtered_response = LiveNewsResource(all_categories_resp)._getCategoriesFormatted()._filterCategories(self.__excludeCategories)._response
            self.__validCategoriesList = json.loads(filtered_response)['data']['categories']
            return filtered_response
        else:
            return all_categories_resp

    @Validator.isRequired(['category'])
    def _getGeneralNews(self, category : str, searchText : str = None, pageNumber : int = None) -> str :
        LOGGER.debug("inside _getGeneralNews method")
        response = ""

        self._getNewsCategories()

        if self.__validCategoriesList:
            specific_cat_dict, special = self.__getSpecificCategoryData(category)

            if specific_cat_dict :
                request_body = {
                    "exclCategory": [] if special else specific_cat_dict["exc"],
                    "inclCategory": [specific_cat_dict["cat"]] if special else specific_cat_dict["inc"],
                    "validRequest": None if special else specific_cat_dict["lgrq"],
                    "page": pageNumber,
                    "group": specific_cat_dict['uiTyp'],
                    "searchText": searchText
                }
                response = self.__getGeneralNewsAPI(request_body)
                if response != '""':
                    response = LiveNewsResource(response, specific_cat_dict['uiTyp'])._getNewsFormatted()._response
        return response

    def _getHoldingsNews(self, category : Union[str, list] = None, searchText : str = None, pageNumber : int = None) -> str :
        LOGGER.debug("inside _getHoldingsNews method")
        response = ""
        category_list = []
        if category:
            category_list.extend(category) if type(category) is list else category_list.append(category)

        self._getNewsCategories()
        if self.__validCategoriesList:
            holdings_cat_data, _ = self.__getSpecificCategoryData("My Holdings", True)
            request_body = {
                "exclCategory": holdings_cat_data["exc"],
                "inclCategory": holdings_cat_data["inc"],
                "validRequest": holdings_cat_data["lgrq"],
                "group": holdings_cat_data["uiTyp"],
                "page": pageNumber,
                "searchText": searchText
            }

            response = self.__getHoldingsNewsAPI(request_body)

            if response != '""':
                response = LiveNewsResource(response, holdings_cat_data["uiTyp"])._getNewsFormatted()._response

                if category and category != "All" : # if category is All, no filtering required

                    if sorted(category) == sorted([e.value for e in ResultsAndStocksNewsCategoryEnum]):
                        self.__validCategoriesList = [e.value for e in ResultsAndStocksNewsCategoryEnum]

                    filter_categories = []
                    for cat in category_list :
                        cat_dict, special = self.__getSpecificCategoryData(cat)
                        filter_categories.append(cat_dict["cat"]) if special else filter_categories.extend(cat_dict["inc"])

                    response = LiveNewsResource(response, category_dp_name=category)._filterCategories(filter_categories, exclude=False)._response

        return response

    def _getResultsAndStocksNews(self, searchText : str = None, pageNumber : int = None) -> str :
        LOGGER.debug("inside _getResultsAndStocksNews method")
        response = ""

        request_body = {
            "exclCategory": [],
            "inclCategory": ["Result", "STOCK_IN_NEWS"],
            "validRequest":  False,
            "page": pageNumber,
            "group": "G",
            "searchText": searchText
        }
        response = self.__getGeneralNewsAPI(request_body)
        if response != '""':
            response = LiveNewsResource(response, "G")._getNewsFormatted()._response
        return response


    def __getSpecificCategoryData(self, category : str, holdings : bool = False) -> Tuple[dict, bool]:
        LOGGER.debug("inside __getSpecificCategoryData method")
        cat_data = {}
        special = False
        if self.__allCategoriesDataDict :
            if holdings or category in self.__validCategoriesList :
                for key, value in self.__allCategoriesDataDict['data'].items():
                    if type(value) is list:
                        for cat_dict in value:
                            if 'dpNm' in cat_dict.keys() and cat_dict['dpNm'] == category:
                                if key == "ctLst":
                                    special = True
                                cat_data = cat_dict
                                break
            else :
                raise ValidationException(f"'{category}' is not a valid category. Please call getNewsCategories function to retrieve all valid categories.")

        return cat_data, special

    def __getAllNewsCategories(self) -> str:
        '''method to either read all categories from user session file or get all categories from categories API'''
        LOGGER.debug("inside __getAllNewsCategories method")

        try:
            with open(self.__fileName, 'r+') as fs:
                read = fs.read()
                user_data_dict = json.loads(read)
                # if categories saved in data_ApiKey.txt file
                if 'newsCategories' in user_data_dict.keys():
                    LOGGER.debug(f"Reading categories response from user data file." )
                    self.__allCategoriesDataDict = user_data_dict['newsCategories']
                    newsCategoriesResponse = json.dumps(self.__allCategoriesDataDict)
                # if categories not saved in file, call api and save response in data_ApiKey.txt
                else :
                    newsCategoriesResponse = self.__getAllNewsCategoriesAPI()
                    if newsCategoriesResponse != "":
                        self.__allCategoriesDataDict = json.loads(newsCategoriesResponse)
                        user_data_dict['newsCategories'] = self.__allCategoriesDataDict
                        # deleting contents of data_ApiKey.txt and writing categories-appended-data
                        fs.seek(0)
                        fs.truncate()
                        fs.write(json.dumps(user_data_dict))
                        LOGGER.debug("Categories response saved to user data file.")
            return newsCategoriesResponse
        except FileNotFoundError:
            LOGGER.error(f"Session file {self.__fileName} not found. Kindly login again.")
            raise APIError("Session file not found. Kindly login again.")
        except OSError as e:
            LOGGER.error(f"Error in reading/writing {self.__fileName} : {e}")
            raise e

    def __getAllNewsCategoriesAPI(self) -> str:

        LOGGER.debug("inside __getAllNewsCategoriesAPI method")

        url = self.__routerObj._LiveNewsCategoriesURL()
        reply = self.__http._GetMethod(url)
        LOGGER.debug(f"Response received: {reply}")

        return json.dumps(reply)

    def __getGeneralNewsAPI(self, request_body) -> str:

        LOGGER.debug("inside __getGeneralNewsAPI method")

        url = self.__routerObj._GeneralNewsURL()
        body = json.dumps(request_body)

        LOGGER.debug("__getGeneralNewsAPI method is called with data: %s", body)
        reply = self.__http._PostMethod(url, body)
        LOGGER.debug(f"Response received: {reply}")

        return json.dumps(reply)

    def __getHoldingsNewsAPI(self, request_body ) -> str:

        LOGGER.debug("inside __getHoldingsNewsAPI method")
        url = self.__routerObj._HoldingsNewsURL()
        body = json.dumps(request_body)

        LOGGER.debug("__getHoldingsNewsAPI method is called with data: %s", body)
        reply = self.__http._PostMethod(url, body)
        LOGGER.debug(f"Response received: {reply}")

        return json.dumps(reply)

    def _getLatestCorpActionsAPI(self, symbol : str) -> str:

        LOGGER.debug("inside __getLatestCorpActionsAPI method")
        url = self.__routerObj._LatestCorpActionsURL().format(symbol = symbol)
        reply = self.__http._GetMethod(url)
        LOGGER.debug(f"Response received: {reply}")

        return json.dumps(reply)