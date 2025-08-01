# StopCriterion Package

This package contains all the stop criterion types provided by **pyHarm**. It is organized around an abstract class, **ABCStopCriterion**, and a **FactoryStopCriterion** that is responsible for creating the objects. All stop criterion objects must adhere to the **ABCStopCriterion** abstract class. A brief description of the modules provided in this subpackage is given below:

- **`ABCStopCriterion.py`**: The **ABCStopCriterion** class is an abstract class defining the essential components of any stop criterion. One abstract method is defined.
- **`FactoryStopCriterion.py`**: Contains the dictionary of all available stop criteria and the `generateStopCriterion` function, which creates the criterion object based on the selected keyword.
- **`StopCriterionBounds.py`**: Activates the criterion if the bounds of angular frequency are reached (either lower or upper).
- **`StopCriterionBoundsOrSolNumber.py`**: Activates the criterion either if the bounds of angular frequency are reached, or if the provided maximum number of solutions is reached.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/StopCriterion.html).