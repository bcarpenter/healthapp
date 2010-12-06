double** calculateJacobian(double* varValues, double (**funcs)(double* values), double epsilon, int length) {
  /**
   * Assumes that the number of variables and number of functions are the same
   */
  double** matrix = (double**) malloc(sizeof(double*) * length);

  // the double delta varaiable values
  double deltaVarValues[length];

  int i;
  int index;
  for (i = 0; i < length; i++) {
    deltaVarValues[i] = varValues[i];
  }


  for (i = 0; i < length; i++) {
    double* row = (double*) malloc(sizeof(double) * length);

    if (row == NULL) {
      // error
    }

    double originalValue = funcs[i](varValues);

    for (index = 0; index < length; index++) {
      if (index == 0)
        deltaVarValues[length - 1] = varValues[length - 1];
      else
        deltaVarValues[index - 1] = varValues[index - 1];
      deltaVarValues[index] += epsilon;

      double value = (funcs[i](deltaVarValues) - originalValue)/epsilon;
      row[index] = value;
    }

    matrix[i] = row;
  }

  return matrix;
}
void toReducedRowEchelonForm(double** matrix, int rowCount, int columnCount) {

	int lead = 0;	
	int r;
	for (r = 0; r < rowCount; r++) {
		if (columnCount <= lead)
			return;
		int i = r;
		while (matrix[i][lead] == 0) {
			i++;
			if (rowCount == i) {
				i = r;
				lead ++;
				if (columnCount == lead)
					return;
			}
		}
		
		if (i != r) {
			double* tempRow = matrix[i];
			matrix[i] = matrix[r];
			matrix[r] = tempRow;
		}
		
		double value = matrix[r][lead];
		
		// assert value != 0... it should be 1
		
		int index;
		for (index = 0; index < columnCount; index++) {
			matrix[r][index] /= value;
		}
		
		for (i = 0; i < rowCount; i++) {
			if (i != r) {
				double leadValue = matrix[i][lead];
				for (index = 0; index < columnCount; index++) {
					matrix[i][index] -= leadValue * matrix[r][index];
				}
			}
		}
		lead++;
	}
	return;
}

double* linearSolver(double** A, double* values, int length) {
	/**
	 * Assumptions:
	 * - A is a <length> by <length> 2d matrix of doubles
	 * - values is a <length> 1d matrix of doubles
	 */ 
	// TODO: some copying inefficiencies here (maybe)
	double** extendedA = (double**) malloc(sizeof(double*) * length);
	double* solutions = (double*) malloc(sizeof(double) * length);
	
	
	
	if (extendedA == NULL || solutions == NULL) {
		
	}
		
	int i, j;
	for (i = 0; i < length; i++) {
		double* row = (double*)  malloc(sizeof(double) * (length+1));
		if (row == NULL) {
		
		}
		for (j = 0; j < length; j++) {
			row[j] = A[i][j];
		}
		row[length] = values[i];
		
		extendedA[i] = row;
	}

	toReducedRowEchelonForm(extendedA, length, length+1);

	for (i = 0; i < length; i++) {
		solutions[i] = extendedA[i][length];
		free(extendedA[i]);
	}
	free(extendedA);

	return solutions;	
}
double* newtonsMethod(double (**funcs)(double* values), double* initialXs, int length, double epsilon, int maxIters) {
	
	int iters, i;
	
	// current value of our variables
	double* x = (double*) malloc(sizeof(double) * length);
	double g[length];
	double oldX[length];
	
	if (x == NULL) {
	
	}
	
	for (i = 0; i < length; i++) {
		x[i] = initialXs[i];
	}
	
	for (iters = 0; iters < maxIters; iters++) {
		for (i = 0; i < length; i++) {
			oldX[i] = x[i]; 
			g[i] = -funcs[i](x);
		}
		
		double** H = calculateJacobian(x, funcs, epsilon, length);

		double* v = linearSolver(H, g, length);

		for (i = 0; i < length; i++) {
			x[i] += v[i];
		}
		
		double delta = 0;
		
		for (i = 0; i < length; i++) {
			delta += pow(oldX[i]- x[i], 2);
		}
		delta = sqrt(delta);
		
		if (delta <= epsilon)
			break;
	}
	
	return x;
}


void newtonsMethod_in_c(PyObject* initialGuesses, PyObject* solutions, PyObject* epsilon, PyObject* maxIters)
{
		
        double initialXs[${length}];
        //double* initialXs = (double *) PyArray_DATA(initialGuesses);
        double (*funcs[${length}]) (double* values);
        
        
		for (int i=0; i<${length}; i++)
		{	
			PyObject* item = PySequence_GetItem(initialGuesses, i);

            // convert python array to c array
            initialXs[i] = PyFloat_AsDouble(item);

		}

        % for i in range(0, length):
            funcs[${i}] = func${i};
        % endfor
        
        double c_epsilon = PyFloat_AsDouble(epsilon);
        int c_maxIters = PyLong_AsLong(maxIters);

        //double* _my_out_grid = (double *) PyArray_DATA(solutions);

        //printf("calculating solution\n");
        //printf("%f\n", initialXs[0]);
        double* c_solution = newtonsMethod(funcs, initialXs, ${length}, c_epsilon, c_maxIters);
        //printf("done calculating solution\n");
        //solutions = (PyObject*)c_solution;
        Py_ssize_t index = 0;
        
        for (int i=0; i<${length}; i++)
		{
            PySequence_SetItem(solutions, index, PyFloat_FromDouble(c_solution[i]));
            index++;
            //_my_out_grid[i] = c_solution[i];
            //printf("%f\n", _my_out_grid[i]);
		}

		// return new_arr;

}
