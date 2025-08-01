from exceptions.api_exception import APIError


class ValidationException(APIError):

    def __init__(self, msg = '', *args, **kwargs) -> None:
        HTTP_UNPROCESSABLE_ENTITY  = 422
        self.msg = msg
        self.err_code = HTTP_UNPROCESSABLE_ENTITY
        super().__init__(msg, *args, **kwargs)

    def __str__(self):
        return(f"Error {self.err_code} : {self.msg}")
