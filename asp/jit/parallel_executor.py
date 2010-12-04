from collections import defaultdict, namedtuple
from asp_module import ASPModule
from ..codegen.templating.template import indent, Template

Task = namedtuple('Task', 'name args')

class ParallelExecutor(object):

    def __init__(self, *args):
        self.kernels = [a for a in args if a is not None]
        self.asp_module = TracingModule()
        for kernel in self.kernels:
            kernel.asp_module_factory = lambda: self.asp_module
        self.template = Template(filename='templates/parallel_executor.mako')

    def execute(self):
        if not self.asp_module.arguments:
            return

        tasks, all_arguments = [], []
        for name in self.asp_module.arguments:
            counter = 0
            for args, kwargs in self.asp_module.arguments[name]:
                all_arguments.extend(args)
                all_arguments.extend(kwargs.values())
                arg_count = len(args) + len(kwargs)
                params = ['%s_%d' % (name[:3], ii)
                          for ii in range(counter, counter + arg_count)]
                counter += arg_count
                tasks.append(Task(name, params))

        executor_code = indent(self.template.render(tasks=tasks), '  ')

        self.asp_module.tracing = False
        try:
            self.asp_module.add_function(executor_code, fname='execute')
            self.asp_module.execute(*all_arguments)
        finally:
            self.asp_module.tracing = True
            self.asp_module.clear_traces()

class TracingModule(ASPModule):

    def __init__(self, *args, **kwargs):
        ASPModule.__init__(self, *args, **kwargs)
        self.arguments = defaultdict(list)
        self.tracing = True

    def clear_traces(self):
        self.arguments = defaultdict(list)

    def __getattr__(self, name):
        if self.tracing:
            return self._tracer(name)
        return ASPModule.__getattr__(self, name)

    def _tracer(self, name):
        def trace(*args, **kwargs):
            self.arguments[name].append((args, kwargs))
        return trace

