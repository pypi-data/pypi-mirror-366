# Package Systems

This package contains all the system types provided by **pyHarm**. It is organized around an abstract class, **ABCSystem**, and a **FactorySystem** responsible for instantiating the objects. All system objects must adhere to the **ABCSystem** abstract class. The section below presents the different modules that are available:

- **`ABCSystem.py`**: The **ABCSystem** class is an abstract class defining the essential components of any system. Two abstract methods are mandatory.
- **`FactorySystem.py`**: Contains the dictionary of all available systems and the `generateSystem` function, which creates the **ABCSystem** object. The `System_dico` attribute defined in this module gathers all the **ABCSystem** subclasses available for creation.
- **`System.py`**: The basic system class that implements the computation of `Residual` and `Jacobian` methods by chaining `_residual` and `_jacobian` methods onto the different lists of elements.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Systems.html).