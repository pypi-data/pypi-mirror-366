# Elements Package

An Element in pyHarm is defined as any object that contributes to the residual equation and its Jacobian. Each element inherits from the `ABCElement` abstract class. This package consists of the following modules:

- **`ABCElement.py`**: The `ABCElement` class serves as the abstract class governing the definition of an element in pyHarm. It is implemented with generic methods that are useful for all other elements.
- **`FactoryElements.py`**: The `FactoryElements` module acts as the factory for creating Elements in pyHarm. It comprises a dictionary that contains references to all available and instantiable elements in pyHarm, with the key being the `factory_keyword` property defined in each instantiable element, and the reference to the class as the value. The generation of the `ABCElement` subclass is facilitated through the `generateElement` function.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Elements.html).