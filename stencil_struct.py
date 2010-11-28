class StencilStruct(object):

    def __init__(self, fields, data):
        if len(data) != len(fields):
            raise Exception('data must match number of fields')
        self._fields = fields
        self.data = data

    def __getattribute__(self, name):
        try:
            index = fields.index(name)
        except ValueError:
            return object.__getattribute__(self, name)
        return self.data[index]

    def __setattr__(self, name, value):
        try:
            index = fields.index(name)
        except ValueError:
            object.__setattribute__(self, name, value)
        else:
            self.data[index] = value

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    @staticmethod
    def struct_from_fields(fields):
        return lambda data: StencilStruct(fields, data)
