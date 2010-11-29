class StencilStruct(object):

    def __init__(self, dtype, data):
        if len(data) != len(dtype.names):
            raise Exception('data must match number of fields')
        self._fields = tuple(dtype.names)
        self.data = data

    def __getattr__(self, name):
        try:
            return self.data[name]
        except IndexError:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in ('_fields', 'data'):
            object.__setattr__(self, name, value)
        else:
            try:
                self.data[name] = value
            except IndexError:
                object.__setattr__(self, name, value)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return 'StencilStruct(%s, %s)' % (self._fields, tuple(self.data))

    @staticmethod
    def struct_from_fields(fields):
        class Struct(StencilStruct):

            _fields = tuple(fields)

            def __init__(self, data):
                StencilStruct.__init__(self, Struct._fields, data)

        return Struct
