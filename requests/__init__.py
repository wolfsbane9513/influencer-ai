class Response:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json

def post(*args, **kwargs):
    return Response()

def get(*args, **kwargs):
    return Response()
