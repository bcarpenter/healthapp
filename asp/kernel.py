from collections import defaultdict

class Kernel(object):

    __initialized_modules = defaultdict(set)
    __kernel_ids = defaultdict(lambda: 0)

    def __init__(self):
        self.id = Kernel.__kernel_id()

    @classmethod
    def __kernel_id(cls):
        kernel_id = Kernel.__kernel_ids[cls.__name__]
        Kernel.__kernel_ids[cls.__name__] += 1
        name = Kernel.escape_class_name(cls.__name__)
        return '{name}_{id}'.format(name=name, id=kernel_id)

    @classmethod
    def is_initialized(cls, module):
        return module in Kernel.__initialized_modules[cls]

    @classmethod
    def mark_initialized(cls, module):
        """Remembers that an ASP module has been initialized by the current
        kernel class. This is so that multiple instances of the same kernel
        type can add functions to the same module without resulting in multiple
        initializations.
        """
        Kernel.__initialized_modules[cls].add(module)
        for base_class in cls.__bases__:
            if issubclass(base_class, Kernel):
                base_class.mark_initialized(module)

    @staticmethod
    def escape_class_name(name):
        return name.replace('_', '__').replace('.', '_')
