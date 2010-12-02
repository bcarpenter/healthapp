class NewtonsMethod(object):
    
    def __init__(self):
        self.pure_python = True

    def iterate_using_template(self, functionsFile, initialGuesses, max_iters=100, epsilon=0.0001):
        import asp.codegen.templating.template as template
        mytemplate = template.Template(filename="templates/newtonsMethod_template.mako")
        rendered = mytemplate.render(length=len(initialGuesses),funcsPath=functionsFile)
    
        import asp.jit.asp_module as asp_module
        mod = asp_module.ASPModule()
        # remember, must specify function name when using a string
        mod.add_function(rendered, fname="newtonsMethod_in_c")
        result =  mod.newtonsMethod_in_c(initialGuesses, epsilon, max_iters)
        return result

    def iterate(self, functionsFile, initialGuesses, max_iters=100, epsilon=0.0001):
        pass
        

