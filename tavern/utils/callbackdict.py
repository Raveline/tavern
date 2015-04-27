class CallbackDict(dict):
    """
    A dict that calls a callback method when
    its value are updated.
    """

    def __init__(self, callback, iterable):
        """
        Only build using an already existing dict.
        """
        super(CallbackDict, self).__init__(iterable)
        self.callback = callback

    def __setitem__(self, key, value):
        super(CallbackDict, self).__setitem__(key, value)
        self.callback()
