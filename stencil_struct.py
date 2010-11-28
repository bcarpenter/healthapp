class StencilStruct(object):

    def __init__(self, fields, data):
        if len(data) != len(fields):
            raise Exception('data must match number of fields')
        self._fields = tuple(fields)
        self.data = data

    def __getattr__(self, name):
        try:
            index = self._fields.index(name)
        except ValueError:
            return object.__getattribute__(self, name)
        return self.data[index]

    def __setattr__(self, name, value):
        if name in ('_fields', 'data'):
            object.__setattr__(self, name, value)
        else:
            try:
                index = self._fields.index(name)
            except ValueError:
                object.__setattr__(self, name, value)
            else:
                self.data[index] = value

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return 'StencilStruct(%s, %s)' % (self._fields, tuple(self.data))

    @staticmethod
    def struct_from_fields(fields):
        struct_fields = tuple(fields)
        return lambda data: StencilStruct(struct_fields, data)
