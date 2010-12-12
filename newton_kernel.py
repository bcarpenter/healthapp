import numpy
import inspect
import asp.codegen.python_ast as ast
import asp.codegen.cpp_ast as cpp_ast
import asp.codegen.ast_tools as ast_tools
from asp.kernel import Kernel
from asp.util import *
from newtons_method import *

class NewtonKernel(Kernel):

    def __init__(self, asp_module_factory=None):
        # we want to raise an exception if there is no kernel()
        # method defined.
        try:
            dir(self).index("kernel")
        except ValueError:
            raise Exception("No kernel method defined.")

        # if the method is defined, let us introspect and find
        # its AST
        self.kernel_src = inspect.getsource(self.kernel)
        self.kernel_ast = ast.parse(self.remove_indentation(self.kernel_src))

        self.pure_python = False
        self.pure_python_kernel = self.kernel

        # replace kernel with shadow version
        self.kernel = self.shadow_kernel
        if asp_module_factory is None:
            from asp.jit import asp_module
            self.asp_module_factory = asp_module.ASPModule
        else:
            self.asp_module_factory = asp_module_factory
    def solve(self, functions, initialGuesses, solution, max_iters=100, epsilon=0.0001):
        return NewtonsMethod().iterate(functions, initialGuesses, solution, max_iters=100, epsilon=0.0001)
    def remove_indentation(self, src):
        return src.lstrip()

    def add_libraries(self, mod):
        """Adds the necessary gcc includes, headers, and initialization calls
        to use the numpy C API.
        """
        if not NewtonKernel.is_initialized(mod):
            mod.add_library('numpy', [numpy.get_include() + '/numpy'])
            mod.add_header('arrayobject.h')
            mod.add_header('math.h')
            mod.add_to_init([cpp_ast.Statement('import_array()')])
            NewtonKernel.mark_initialized(mod)
    def processFunctions(self, mod):
        index = 0
        math_funcs = []
        while hasattr(self, "func"+str(index)):
            math_funcs.append("func"+str(index))

            func_src = inspect.getsource(getattr(self, "func"+str(index)))
            func_ast = ast.parse(self.remove_indentation(func_src))

            phase2 = NewtonKernel.NewtonProcessAST({}).visit(func_ast)
            phase3 = NewtonKernel.NewtonConvertAST({}).visit(phase2)
        
            mod.add_function(phase3, fname="func"+str(index))#rendered)
            index+=1
        return index
    def shadow_kernel(self, *args):
        if self.pure_python:
            return self.pure_python_kernel(*args)

        #FIXME: need to somehow match arg names to args
        argnames = map(lambda x: str(x.id), self.kernel_ast.body[0].args.args)
        argdict = dict(zip(argnames[1:], args))
        
        phase2 = NewtonKernel.NewtonProcessAST(argdict).visit(self.kernel_ast)
  
        curList = []
        def flattenAST(ast, lst):
            if isinstance(ast, list):
                for node in ast:
                    flattenAST(node, lst)
            elif isinstance(ast, phase2.body[0].__class__):
                lst.append(ast)
                def extractFunctions(fDef):
                    extractedList = []
                    removeList = []
                    for node in fDef.body:
                        if isinstance(node, NewtonKernel.MathFunctionDef):
                            extractedList.append(node)                            
                            removeList.append(node)
                    for item in removeList:
                        fDef.body.remove(item)
                    return extractedList
                lst.extend(extractFunctions(ast))
                #lst[0].body = [ast_tools.Call("newtonsMethod_in_c", ["initialGuess", "epsilon", "max_iters"])]
                lst.append(lst[0])
                lst.remove(lst[0])
            return lst
        phase2.body= flattenAST(phase2.body, [])

        debug_print('Phase 2 AST:\n' + ast.dump(phase2))
       
        phase3 = NewtonKernel.NewtonConvertAST(argdict).visit(phase2)
       
        import asp.codegen.templating.template as template
        mod = self.asp_module_factory()
        self.add_libraries(mod)
        index = self.processFunctions(mod)
        mytemplate = template.Template(filename="templates/test.c")
        rendered = mytemplate.render(length=2)

        # remember, must specify function name when using a string
        for ast_func in phase2.body[:-1]:
            mod.add_function(NewtonKernel.NewtonConvertAST(argdict).visit(ast_func))
        mod.add_function(rendered, fname="newtonsMethod_in_c")
        #mod.add_function(NewtonKernel.NewtonConvertAST(argdict).visit(phase2.body[-1]))

        #newtonsMethod_in_c = open(templates/test.c")
        #mod.add_function(newtonsMethod_in_c, fname="newtonsMethod_in_c")
        #mod.add_function(phase3)
        #mod.add_function(NewtonKernel.NewtonConvertAST(argdict).visit(phase2.body[1]))
        #mod.kernel(*grid_data)
        #mod.func0(1)
        #mod.add_function(phase3, fname="func"+str(index))#rendered)
        initialXs = args[0]
        solution = args[1]
        npInitialXs = numpy.zeros(len(initialXs), float)
        for i in range(len(initialXs)):
            npInitialXs[i] = initialXs[i]
        npSolution =  numpy.zeros(len(solution), float)
        real_args = [args[0], args[1], args[2], args[3]]
        mod.newtonsMethod_in_c(*real_args)
        #for i in range(len(solution)):
        #    solution[i] = npSolution[i]
            #print solution[i]
    # the actual Stencil AST Node
    class SquareRoot(ast.AST):
        def __init__(self, value):
          self.value = value
          self._fields = ('value')

          super(NewtonKernel.MathFunction, self).__init__()
    
    # the actual Stencil AST Node
    class Power(ast.AST):
        def __init__(self, value, power):
          self.value = value
          self.power = power      
          self._fields = ('value', 'power')

          super(NewtonKernel.VariableList, self).__init__()
    class MathFunctionDef(ast.AST):
        def __init__(self, orig_node, name, arg, body):
          self.name = name
          self.arg = arg
          self.body = body
          self.orig_node = orig_node
          self._fields = ('orig_node','name', 'body')  

    class ReturnCheater(ast.AST):
        def __init__(self, strExpr):
            self.value = strExpr
    # separate files for different architectures
    # class to convert from Python AST to an AST with special Stencil node
    class NewtonProcessAST(ast.NodeTransformer):
        def __init__(self, argdict):
            self.argdict = argdict
            super(NewtonKernel.NewtonProcessAST, self).__init__()
        """
        def visit_Call(self, node):
            return node
            print ("visiting call...\n")
            print node.func.id
            return ast_tools.Call(node.func, node.args)
            if (node.func.id == "NewtonsMethod"):
                print("Found something to change...\n")
                # node.
                newNode = NewtonKernel.NewtonsMethodCall()
                return node
            elif (node.func.__class__.__name__ == "sqrt"):
                return node
            elif (node.func.__class__.__name__ == "pow"):
                return node
            else:
                return node
        """   
        def visit_FunctionDef (self, node):
            #return node
            if node.name.startswith("func") and len(node.args.args):
                body = node.body
                #body = map(self.visit, node.body)
                newnode = NewtonKernel.MathFunctionDef(node, node.name,node.args.args[0].id, body)
                #newnode = ast_tools.ConvertAST.visit_FunctionDef(self, node, "double")
                return newnode
            else:
                if isinstance(node.body, list):
                    node.body = [self.visit(item) for item in node.body]
                return node
        """
        def visit_Return(self, node):
            print "\n\n\n\n\n READ \n\n\n\n\n"
            print dir(node.value)
            print node.value
            return NewtonKernel.ReturnCheater(node.value)


        def visit_FunctionDef (self, node):
            #return node
            if node.name.startswith("func") and len(node.args.args):
                print "in func"
                print dir(node.body[0])
                print node.body[0].value
                body = node.body
                #body = map(self.visit, node.body)
                print dir(node.args.args[0])
                print node.args.args[0].id
                print "body", body
                newnode = NewtonKernel.MathFunctionDef(node, node.name,node.args.args[0].id, body)
                #newnode = ast_tools.ConvertAST.visit_FunctionDef(self, node, "double")
                return newnode
            else:
                if isinstance(node.body, list):
                    node.body = [self.visit(item) for item in node.body]
                return node
        
        def visit_Call(self, node):
            debug_print("visiting a For...\n")
            # check if this is the right kind of For loop
            if (node.iter.__class__.__name__ == "Call" and
                node.iter.func.__class__.__name__ == "Attribute"):
                
                debug_print("Found something to change...\n")

                if (node.iter.func.attr == "interior_points"):
                    grid = self.visit(node.iter.func.value).id       # do we need the name of the grid, or the obj itself?
                    target = self.visit(node.target)
                    body = map(self.visit, node.body)
                    newnode = NewtonKernel.StencilInteriorIter(grid, body, target)
                    return newnode

                elif (node.iter.func.attr == "neighbors"):
                    debug_print(ast.dump(node) + "\n")
                    target = self.visit(node.target)
                    body = map(self.visit, node.body)
                    grid = self.visit(node.iter.func.value).id
                    dist = self.visit(node.iter.args[1]).n
                    newnode = NewtonKernel.StencilNeighborIter(grid, body, target, dist)
                    return newnode

                else:
                    return node
            else:
                return node
        """
    class NewtonConvertAST(ast_tools.ConvertAST):
        
        def __init__(self, argdict):
            super(NewtonKernel.NewtonConvertAST, self).__init__()

        # all arguments are PyObjects
        def visit_arguments(self, node):
            if node.args[0].id == "self":
                return [cpp_ast.Pointer(cpp_ast.Value("PyObject", self.visit(x))) for x in node.args[1:]]
            else:
                return [cpp_ast.Pointer(cpp_ast.Value("double", self.visit(x))) for x in node.args]
        
        def visit_MathFunctionDef(self, node):
            return ast_tools.ConvertAST.visit_FunctionDef(self, node.orig_node, return_type="double")#, args={"double*": node.arg})

        def visit_Power(self, node):
            block = cpp_ast.Block()
            value = self.visit(node.value)
            block.append(cpp_ast.Call("pow", value))
           
            return block
