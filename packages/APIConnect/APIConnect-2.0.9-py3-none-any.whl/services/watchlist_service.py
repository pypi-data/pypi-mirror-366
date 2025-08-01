import json
import logging
import sys
import time
from typing import List
from APIConnect.api_constants import ApiConstants
from APIConnect.http import Http
from constants.router import Router
from resources.watchlist_resource import WatchlistResource

LOGGER = logging.getLogger(__name__)

class WatchlistService:
    def __init__(self, routerObj, httpObj, constantsObj) -> None:
        LOGGER.debug("WatchlistService object is being created.")

        self.__routerObj : Router = routerObj
        self.__http : Http = httpObj
        self.__constants : ApiConstants = constantsObj
        self.__accId = None
        self.__accType = None
        self.__profileId = None

    def _getWatchlistGroups(self) -> str :
        LOGGER.debug("inside _getWatchlistGroups method")

        self.__getUserAccData()

        url = self.__routerObj._WatchlistBaseGroupsURL()
        queryParams = {"accId" : self.__accId, "accTyp" : self.__accType}

        response = self.__getGroupsWatchlistAPI(url, queryParams)
        if response :
            formatted_resp = WatchlistResource(response)._getWatchlistFormatted()._response
            return formatted_resp
        return response

    def _getScripsOfGroup(self, GroupName : str) -> str :
        LOGGER.debug("inside _getScripsOfGroup method")

        self.__getUserAccData()

        url = self.__routerObj._WatchlistGetScripsURL()
        queryParams = {"accId" : self.__accId, "accTyp" : self.__accType, "prfId" : self.__profileId, "grpNm" : GroupName}

        response = self.__getScripsOfGroupAPI(url, queryParams)
        if response :
            formatted_resp = WatchlistResource(response)._getWatchlistFormatted()._response
            return formatted_resp
        return response

    def _createGroup(self, GroupName : str, Symbols : List[str]) -> str :
        LOGGER.debug("inside _createGroup method")

        self.__getUserAccData()

        url = self.__routerObj._WatchlistGroupNameURL().format(groupName = GroupName)
        request_body = {
                        "accId": self.__accId,
                        "accTyp": self.__accType,
                        "prfId": self.__profileId,
                        "grpNm": GroupName,
                        "symLst": Symbols
                        }
        LOGGER.debug(f"_createGroup method is called with data : {request_body}")
        response = self.__createGroupAPI(url, json.dumps(request_body))
        if response :
            formatted_resp = WatchlistResource(response)._getWatchlistFormatted()._response
            return formatted_resp
        return response

    def _addSymbols(self, GroupName : str, Symbols : List[str]) -> str :
        LOGGER.debug("inside _addSymbol method")

        self.__getUserAccData()
        currentUnixTimeStamp = int(time.time()*1000)

        url = self.__routerObj._WatchlistGroupNameURL().format(groupName = GroupName)
        request_body = {
                        "accId": self.__accId,
                        "accTyp": self.__accType,
                        "act": "add",
                        "grpNm": GroupName,
                        "symLst": Symbols,
                        "updatedOn" : currentUnixTimeStamp
                        }
        LOGGER.debug(f"_addSymbol method is called with data : {request_body}")
        response = self.__addSymbolAPI(url, json.dumps(request_body))
        if response :
            formatted_resp = WatchlistResource(response)._getWatchlistFormatted()._response
            return formatted_resp
        return response

    def _deleteSymbols(self, GroupName : str, Symbols : List[str]) -> str :
        LOGGER.debug("inside _deleteSymbols method")

        self.__getUserAccData()
        currentUnixTimeStamp = int(time.time()*1000)

        url = self.__routerObj._WatchlistGroupNameURL().format(groupName = GroupName)
        request_body = {
                        "accId": self.__accId,
                        "accTyp": self.__accType,
                        "act": "del",
                        "grpNm": GroupName,
                        "symLst": Symbols,
                        "updatedOn" : currentUnixTimeStamp
                        }
        LOGGER.debug(f"_deleteSymbols method is called with data : {request_body}")
        response = self.__deleteSymbolAPI(url, json.dumps(request_body))
        if response :
            formatted_resp = WatchlistResource(response)._getWatchlistFormatted()._response
            return formatted_resp
        return response

    def _deleteGroups(self, GroupNames : List[str]) -> str :
        LOGGER.debug("inside _deleteGroups method")

        self.__getUserAccData()

        url = self.__routerObj._WatchlistBaseGroupsURL()
        request_body = {
                        "accId": self.__accId,
                        "accTyp": self.__accType,
                        "prfId": self.__profileId,
                        "delGrp" : GroupNames
                        }
        LOGGER.debug(f"_deleteGroups method is called with data : {request_body}")
        response = self.__deleteGroupsAPI(url, json.dumps(request_body))
        if response :
            formatted_resp = WatchlistResource(response)._getWatchlistFormatted()._response
            return formatted_resp
        return response

    def _renameGroup(self, GroupName : str, NewGroupName : str) -> str :
        LOGGER.debug("inside _renameGroup method")

        oldSymbols = None
        oldGroupSymbolsResponse = self._getScripsOfGroup(GroupName)
        if oldGroupSymbolsResponse :
            oldSymRespDict = json.loads(oldGroupSymbolsResponse)
            symList = oldSymRespDict.get('data').get('syLst')
            if symList:
                oldSymbols = [scrip.get('sym') for scrip in symList if scrip.get('sym')]

        if not oldSymbols:
            LOGGER.error("Failed to retrieve old group data. Please try again.")
            print("Failed to retrieve old group data. Please try again.")
            raise SystemExit(1)

        currentUnixTimeStamp = int(time.time()*1000)

        url = self.__routerObj._WatchlistGroupNameURL().format(groupName = GroupName)
        request_body = {
                        "accId": self.__accId,
                        "accTyp": self.__accType,
                        "act": "modify",
                        "grpNm": GroupName,
                        "newGrpNm": NewGroupName,
                        "symLst": oldSymbols,
                        "updatedOn" : currentUnixTimeStamp
                        }

        LOGGER.debug(f"_renameGroup method is called with data : {request_body}")
        response = self.__renameGroupAPI(url, json.dumps(request_body))
        if response :
            return WatchlistResource(response)._getWatchlistFormatted()._response
        return response

    def __getUserAccData(self) :

        # if user has eq acc id (acc type is EQ or COMEQ)
        if self.__constants.eqAccId :
            self.__accId = self.__constants.eqAccId
            self.__accType = 'EQ'
        # if user has co acc id (acc type is CO)
        elif self.__constants.coAccId :
            self.__accId = self.__constants.coAccId
            self.__accType = 'CO'

        self.__profileId = self.__constants.ProfileId

    def __getGroupsWatchlistAPI(self, url : str, queryParams) -> str:

        LOGGER.debug("inside __getGroupsWatchlistAPI method")

        reply = self.__http._GetMethod(url, queryParams)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply

    def __getScripsOfGroupAPI(self, url : str, queryParams) -> str:

        LOGGER.debug("inside __getScripsOfGroupAPI method")

        reply = self.__http._GetMethod(url, queryParams)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply

    def __createGroupAPI(self, url : str, request_body : str) -> str:

        LOGGER.debug("inside __createGroupAPI method")

        reply = self.__http._PostMethod(url, request_body)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply

    def __addSymbolAPI(self, url : str, request_body : str) -> str:

        LOGGER.debug("inside __addSymbolAPI method")

        reply = self.__http._PutMethod(url, request_body)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply

    def __deleteSymbolAPI(self, url : str, request_body : str) -> str:

        LOGGER.debug("inside __deleteSymbolAPI method")

        reply = self.__http._PutMethod(url, request_body)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply

    def __deleteGroupsAPI(self, url : str, request_body : str) -> str:

        LOGGER.debug("inside __deleteGroupsAPI method")

        reply = self.__http._DeleteMethod(url, request_body)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply

    def __renameGroupAPI(self, url : str, request_body : str) -> str:

        LOGGER.debug("inside __renameGroupAPI method")

        reply = self.__http._PutMethod(url, request_body)

        if reply :
            reply = json.dumps(reply)
        LOGGER.debug(f"Response received : {reply}")
        return reply
