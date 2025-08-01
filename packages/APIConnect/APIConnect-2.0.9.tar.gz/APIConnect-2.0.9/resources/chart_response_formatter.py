class ChartResponseFormatter :
    def __init__(self, response) -> None:
        self.__response_dict = response
        self.__plot_points = self.__response_dict['data']['pltPnts']
        self.__ltt = self.__plot_points['ltt']
        self.__open = self.__plot_points['open']
        self.__high = self.__plot_points['high']
        self.__low = self.__plot_points['low']
        self.__close = self.__plot_points['close']
        self.__vol = self.__plot_points['vol']
        self.__nextTillDate = self.__plot_points['ltt'][0]

    def getOHCLResponse(self) :

        # a list of mapped elements, index wise from all 5 lists
        ltt_o_h_c_l_vol = [list(x) for x in zip(self.__ltt, self.__open, self.__high, self.__low, self.__close, self.__vol)]

        formatted_response_dict = { 'msgID' : self.__response_dict['msgID'],
                                    'srvTm' : self.__response_dict['srvTm'],
                                    'data' : ltt_o_h_c_l_vol,
                                    'nextTillDate' : self.__nextTillDate
                                    }

        return(formatted_response_dict)
    
    def getCustomPeriodOHCLResponse(self) :

        # a list of mapped elements, index wise from all 5 lists
        ltt_o_h_c_l_vol = [list(x) for x in zip(self.__ltt, self.__open, self.__high, self.__low, self.__close, self.__vol)]

        formatted_response_dict = { 'msgID' : self.__response_dict['msgID'],
                                    'srvTm' : self.__response_dict['srvTm'],
                                    'data' : ltt_o_h_c_l_vol
                                  }

        return(formatted_response_dict)