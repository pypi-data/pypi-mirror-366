class MessageResult:
    def __init__(self, response_text: str, success: bool = True, status: int = 200, **kwargs):
        self.response_text = response_text
        self.success = success
        self.status = status
        self.meta = kwargs

    def __str__(self):
        return self.response_text

    def __repr__(self):
        return self.response_text


def get_subclasses(_class, recursive=False):
    subclasses = _class.__subclasses__()
    if not recursive:
        return subclasses
    all_subclasses = subclasses.copy()
    for subclass in subclasses:
        all_subclasses.extend(subclass.get_all_subclasses())
    return all_subclasses
