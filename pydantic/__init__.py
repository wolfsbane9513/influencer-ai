class BaseModel:
    def __init__(self, **data):
        for name, value in self.__class__.__dict__.items():
            if name.startswith('_') or callable(value) or isinstance(value, property):
                continue
            setattr(self, name, data.get(name, value))
        for k, v in data.items():
            if not hasattr(self, k):
                setattr(self, k, v)

def Field(*, default=None, default_factory=None, **kwargs):
    if default_factory is not None:
        return default_factory()
    return default

class BaseSettings(BaseModel):
    pass
