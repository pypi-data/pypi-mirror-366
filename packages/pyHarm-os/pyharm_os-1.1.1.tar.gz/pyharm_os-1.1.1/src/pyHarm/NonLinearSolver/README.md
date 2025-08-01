# Package NonLinearSolver

This package contains all the types of nonlinear solvers provided by **pyHarm**. It is organized around an abstract class, **ABCNLSolver**, and a **FactoryNonLinearSolver** that is responsible for creating the objects. All analysis objects must adhere to the **ABCNLSolver** abstract class. Below is a list of the available modules in this package:

- **`ABCNLSolver.py`**: The **ABCNLSolver** class is an abstract class defining the essential components of any nonlinear solver. One abstract method is defined.
- **`FactoryNonLinearSolver.py`**: Contains the dictionary of all available nonlinear solvers and the `generateNonLinearSolver` function, which creates the nonlinear solver object based on the desired solver type.
- **`ScipyRoot.py`**: This solver wraps the `scipy.optimize.root` function.
- **`NewtonRaphson.py`**: An implementation of a basic Newton-Raphson procedure for solving nonlinear systems iteratively using linear solving techniques.
- **`MoorePenrose.py`**: An implementation of the Moore-Penrose iterative solver. This iterative solver seeks a solution perpendicular to the direction of the previous iteration. It is equivalent to the Newton-Raphson solver with a pseudo-arc length corrector in the first iteration, but the search direction is updated at each iteration.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/NonLinearSolver.html).