from webgraph import Side
from webkernel import JunctionKernel
from newton_kernel import NewtonKernel
from asp import _asp_declare


class InterfaceJunctionKernel(JunctionKernel):

    def junction_values(self, in_junction, out_junction):
        leftSide = []
        rightSide = []
        for num, side in in_junction.line_sides.items():
            if side == Side.LEFT:
                leftSide.append(num)
            elif side == Side.RIGHT:
                rightSide.append(num)

        assert( (len(leftSide) == 1 and len(rightSide) == 2) or
                (len(leftSide) == 2 and len(rightSide) == 1) )
        
        input_side_name = None
        input_side = []
        output_side = []
        if (len(leftSide) == 1):
            input_side = leftSide
            output_side = rightSide
            input_side_name = Side.LEFT
        else:
            input_side_name = Side.RIGHT
            input_side = rightSide
            output_side = leftSide

        # do calculation
        input_nodes = in_junction.line_values[input_side[0]]
        output_nodes0 = in_junction.line_values[output_side[0]]
        output_nodes1 = in_junction.line_values[output_side[1]]

        junction_input_nodes = input_nodes[1:]
        junction_output_nodes0 = output_nodes0[:-1]
        junction_output_nodes1 = output_nodes1[:-1]
        
        guess = [1, 2, 3, 4, 5, 6]
        solution = [0, 0, 0, 0, 0, 0]
        kernel = JunctionNewtonKernel()
        kernel.pure_python = False
        kernel.kernel(guess, solution, 0.00001, 1000)
        
        # populate solutions into out_junction
        count = 0
        for num in out_junction.line_sides.keys():
            if out_junction.line_sides[num] == Side.LEFT:
                if input_side_name == Side.LEFT:
                    out_junction.line_values[num][0].A = abs(solution[0])
                    out_junction.line_values[num][0].u = abs(solution[3])
                    out_junction.line_values[num][0].p = abs(solution[0]*solution[3]/2)# = leftSide.pop()#StencilStruct(1,2,3)
                else:
                    out_junction.line_values[num][0].A = abs(solution[1+count])
                    out_junction.line_values[num][0].u = abs(solution[4+count])
                    out_junction.line_values[num][0].p = abs(solution[0+count]*solution[3+count]/2)# = leftSide.pop()#StencilStruct(1,2,3)              
                    count+=1              
            elif out_junction.line_sides[num] == Side.RIGHT:
                if input_side_name == Side.RIGHT:
                    out_junction.line_values[num][0].A = abs(solution[0])
                    out_junction.line_values[num][0].u = abs(solution[3])
                    out_junction.line_values[num][0].p = abs(solution[0]*solution[3]/2)# = leftSide.pop()#StencilStruct(1,2,3)
                else:
                    out_junction.line_values[num][0].A = abs(solution[1+count])
                    out_junction.line_values[num][0].u = abs(solution[4+count])
                    out_junction.line_values[num][0].p = abs(solution[1+count]*solution[4+count]/2)# = leftSide.pop()#StencilStruct(1,2,3)
                    count+=1
            else:
                raise Exception('unknown side')


class JunctionNewtonKernel(NewtonKernel):

    def kernel(self, initialGuess, solution, epsilon, max_iters):
        # x:
        # - x[0] = a1_star
        # - x[1] = a2_star
        # - x[2] = a3_star
        # - x[3] = u1_star
        # - x[4] = u2_star
        # - x[5] = u3_star

        def func0(x):
            return x[3]*x[0] - (x[4]*x[1] + x[5]*x[2])

        def func1(x):
            _asp_declare('double', 'rho')
            _asp_declare('double', 'b1_1')
            _asp_declare('double', 'b1_2')
            _asp_declare('double', 'b1_3')
            _asp_declare('double', 'A_0_1')
            _asp_declare('double', 'A_0_2')
            _asp_declare('double', 'A_0_3')
            rho = 1
            b1_1 = 2
            b1_2 = 3            
            b1_3 = 4      
            A_0_1 = 5
            A_0_2 = 6
            A_0_3 = 7
            return (b1_1 / A_0_1 * x[0] -
                    b1_2 / A_0_2 * x[1] * .5 * rho *
                    (pow(x[3], 2) - pow(x[4], 2)))

        def func2(x):
            _asp_declare('double', 'rho')
            _asp_declare('double', 'b1_1')
            _asp_declare('double', 'b1_2')
            _asp_declare('double', 'b1_3')
            _asp_declare('double', 'A_0_1')
            _asp_declare('double', 'A_0_2')
            _asp_declare('double', 'A_0_3')
            rho = 1
            b1_1 = 2
            b1_2 = 3           
            b1_3 = 4      
            A_0_1 = 5
            A_0_2 = 6
            A_0_3 = 7
            return (b1_1 / A_0_1 * x[0] -
                    b1_3 / A_0_2 * x[2] * .5 * rho *
                    (pow(x[3], 2) - pow(x[5], 2)))

        def func3(x):
            _asp_declare('double', 'rho')
            _asp_declare('double', 'b1_1')
            _asp_declare('double', 'b1_2')
            _asp_declare('double', 'b1_3')
            _asp_declare('double', 'A_0_1')
            _asp_declare('double', 'A_0_2')
            _asp_declare('double', 'A_0_3')
            rho = 1
            b1_1 = 2
            b1_2 = 3            
            b1_3 = 4      
            A_0_1 = 5
            A_0_2 = 6
            A_0_3 = 7
            return x[3]+ pow(4 * x[0], 2) * b1_1 / (2 * rho * A_0_1)

        def func4(x):
            _asp_declare('double', 'rho')
            _asp_declare('double', 'b1_1')
            _asp_declare('double', 'b1_2')
            _asp_declare('double', 'b1_3')
            _asp_declare('double', 'A_0_1')
            _asp_declare('double', 'A_0_2')
            _asp_declare('double', 'A_0_3')
            rho = 1
            b1_1 = 2
            b1_2 = 3            
            b1_3 = 4      
            A_0_1 = 5
            A_0_2 = 6
            A_0_3 = 7
            return x[4] + pow(4 * x[1], 2) * b1_2 / (2 * rho * A_0_2)

        def func5(x):
            _asp_declare('double', 'rho')
            _asp_declare('double', 'b1_1')
            _asp_declare('double', 'b1_2')
            _asp_declare('double', 'b1_3')
            _asp_declare('double', 'A_0_1')
            _asp_declare('double', 'A_0_2')
            _asp_declare('double', 'A_0_3')
            rho = 1
            b1_1 = 2
            b1_2 = 3            
            b1_3 = 4      
            A_0_1 = 5
            A_0_2 = 6
            A_0_3 = 7
            return x[5] + pow(4 * x[2], 2) * b1_3 / (2 * rho * A_0_3)

        functions = [func0, func1, func2, func3, func4, func5]
        self.solve(functions, initialGuess, solution, epsilon, max_iters)
