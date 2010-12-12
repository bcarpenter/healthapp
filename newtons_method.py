import math

class NewtonsMethod(object):
    
    def __init__(self):
        self.pure_python = True

    def iterate_using_template(self, functionsFile, initialGuesses, solutions,
                               max_iters=100, epsilon=0.0001):
        import asp.codegen.templating.template as template
        template_file = 'templates/newtonsMethod_template.mako'
        mytemplate = template.Template(filename=template_file)
        rendered = mytemplate.render(length=len(initialGuesses),
                                     funcsPath=functionsFile)
    
        import asp.jit.asp_module as asp_module
        mod = asp_module.ASPModule()
        mod.add_function(rendered, fname="newtonsMethod_in_c")
        mod.newtonsMethod_in_c(initialGuesses, solution, epsilon, max_iters)
        solutions = result

    def iterate(self, functions, initialGuesses, solution,
                max_iters=100, epsilon=0.0001):
        solution_temp = newtonsMethod(functions, max_iters, initialGuesses,
                                      epsilon)
        for i in range(len(solution)):
            solution[i] = solution_temp[i]

def newtonsMethod(funcs, maxIters, initialXs, epsilon):
    x = initialXs
    iters = 0
    g = [float('infinity')] * len(funcs)

    while iters < maxIters:
        oldX = x[:]
        g = [-func(x) for func in funcs]
        H = calculateJacobian(x, funcs, epsilon)
        v = linearSolver(H, g)

        for index in range(len(x)):
            x[index] += v[index]
            done, delta = False, 0
            for index in range(0, len(x)):
                delta += (oldX[index] - x[index]) ** 2
            delta = math.sqrt(delta)

            if delta <= epsilon:
                break
            iters += 1
    return x

def calculateJacobian(x, funcs, epsilon):
    matrix = []
    for func in funcs:
        row = []
        for i in range(len(x)):
            y = clone(x)
            y[i] += epsilon
            # TODO: optimize this
            row.append((func(y)-func(x))/epsilon)
        matrix.append(row)	
    return matrix

def linearSolver(A, values):
    assert(len(A) == len(values))
    
    for index in range(0, len(values)):
        A[index].append(values[index])
    matrix = A
    
    toReducedRowEchelonForm(matrix)
    
    solutions = []
    for index in range(0, len(values)):
        solutions.append(matrix[index][-1])
    return solutions

def toReducedRowEchelonForm(matrix):
    """
    Adapted from wikipedia, kinda. I just translated the pseudocode they had
    """
    lead = 0
    rowCount = len(matrix)
    
    try:
        columnCount = len(matrix[0])
    except:
        raise Exception("Matrix error: " + matrix)
    
    for r in range(0, rowCount):
        if columnCount <= lead:
            return 
        i = r
        while matrix[i][lead] == 0:
            i += 1
            if rowCount == i:
                i = r 
                lead = lead +1
                if columnCount == lead:
                    return 
        if i != r:
            tempRow = matrix[i]
            matrix[i] = matrix[r]
            matrix[r] = tempRow
            
        # divide the row by the lead value to normalize
        value = float(matrix[r][lead])
        for index in range(0, len(matrix[r])):
            matrix[r][index] /= value
        
        for i in range(0, rowCount):
            if i != r:
                leadValue = matrix[i][lead]
                for index in range(0, len(matrix[r])):
                    matrix[i][index] -= leadValue * matrix[r][index]
        lead += 1
