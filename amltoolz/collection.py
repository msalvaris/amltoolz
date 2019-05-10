class Collection(object):
    def __init__(self, update_func):
        self._update_func = update_func
        self._elements = None

    def __dir__(self):
        if self._elements is not None:
            return self.__dict__
        else:
            self.refresh()
            return self.__dict__

    def __getitem__(self, item):
        return self._elements[item]

    def __getattr__(self, item):
        if self._elements is None:
            self.refresh()
        elif item in ["_ipython_canary_method_should_not_exist_", "_repr_mimebundle_"]:
            raise AttributeError
        return self._elements[item]

    def __repr__(self):
        items = ("{!r}".format(self._elements[k]) for k in self._elements)
        return "\n{}\n".format("\n".join(items))

    def __eq__(self, other):
        return self.__dict__ == self.__dict__

    def refresh(self):
        self._elements = self._update_func()
        self.__dict__.update(self._elements)

    def __iter__(self):
        if self._elements is None:
            self.refresh()
        return iter(self._elements.values())

    def __contains__(self, key):
        if self._elements is None:
            self.refresh()
        return key in self._elements
