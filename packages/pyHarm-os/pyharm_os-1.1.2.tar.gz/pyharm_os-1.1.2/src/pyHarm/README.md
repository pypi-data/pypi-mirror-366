# Overview of the Main Package

Welcome to the main package of **pyHarm**, which encompasses the essential modules and packages utilized by pyHarm. This package is structured into four primary modules, each described below:

- **`Maestro.py`**: The `Maestro` class serves as the principal interface between the user and the core components of pyHarm. It primarily functions to generate the system under study and the various analyses required. You can create an instance of this class using an input dictionary that outlines the different elements.

- **`BaseUtilsFuncs.py`**: This file houses a collection of generic yet indispensable functions that are utilized across several modules in pyHarm, including the plugin system.

- **`DynamicOperator.py`**: Within this file, you will find functions that generate the derivative operator as well as the Discrete Fourier Transform (DFT) operators.

- **`CoordinateSystem.py`**: This file contains the `CoordinateSystem` class, which is responsible for defining local coordinate systems in pyHarm.

- **`Solver.py`**: The `Solver` class is defined here, being pivotal as the main data/status-based object that interacts with all other objects within pyHarm. It represents a solution to the residual equations and comprises residual values, displacements at starting and solution points, among other vital information.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Module.html).

Additionally, you can find a brief overview of the subpackages [**here**](https://pyharm-saf.readthedocs.io/en/latest/pyHarm.html), with more detailed information available in the documentation for each subpackage.
