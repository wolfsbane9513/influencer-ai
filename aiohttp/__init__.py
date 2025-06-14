class ClientSession:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, *args, **kwargs):
        class Response:
            status = 200
            async def json(self):
                return {}
        return Response()
class ClientResponse:
    def __init__(self, status=200, data=None):
        self.status = status
        self._data = data or {}
    async def json(self):
        return self._data
