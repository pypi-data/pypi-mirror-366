# SubstructureMatrixElement Package

The `SubstructureMatrixElement` subpackage provides implementations of `ABCElement` that allow the input of a matrix-based residual contribution, affecting an entire substructure. This package is composed of the following modules:

- **`MatrixElement.py`**: The `MatrixElement` class serves as the abstract class governing the definition of an element affecting a whole substructure through a given input matrix. This abstract class inherits from `ABCElement` and implements some abstract methods responsible for creating indices of interest and properly reading the input dictionary.
- **`GeneralOrderMatrixElement.py`**: The `GeneralOrderMatrixElement` is a general linear matrix element application that takes as input information about the time derivative through `dto` and the power of angular frequency to be applied through `dom`.
- **`LinearHystMatrixElement.py`**: The `LinearHystMatrixElement` is derived from `GeneralOrderMatrixElement`, imposing `dto` to 1 and `dom` to 0, allowing for the consideration of linearized hysteretic damping effects.
- **`Substructure.py`**: The `Substructure` class is a `MatrixElement` that generates residual contributions from mass, linear damping, gyroscopic, and rigidity matrices.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/SubstructureMatrixElements.html).