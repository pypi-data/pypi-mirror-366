class APIError(Exception):

    def __init__(self, msg = 'API error occured!', *args, **kwargs) -> None:
        self.msg = msg
        super().__init__(self.msg, *args, **kwargs)
