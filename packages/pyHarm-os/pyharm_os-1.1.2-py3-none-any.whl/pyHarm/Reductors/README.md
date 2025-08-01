# Package Reductors

This package contains all the reductor types provided by **pyHarm**. It is organized around an abstract class, **ABCReductor**, and a **FactoryReductor** that is responsible for creating the objects. All reductor objects must adhere to the **ABCReductor** abstract class. Below is a brief description of each module contained in this package:

- **`ABCReductor.py`**: The **ABCReductor** class is an abstract class defining the essential components of any reductor used in pyHarm. Four abstract methods are defined.
- **`FactoryReductor.py`**: Contains the dictionary of all available reductors and the `generateReductor` function, which creates the reductor object.
- **`ChainReductor.py`**: The **ChainReductor** object is a reductor composed of a list of single reductors. It sequences the operations of `update_reductor`, `expand`, `reduce_vector`, and `reduce_matrix` within the list of reductors.
- **`FactoryChainReductor.py`**: Contains the function `generateChainReductor` that creates the **ChainReductor** object used by the analysis.
- **`NoReductor.py`**: The default reductor that performs no reduction.
- **`KrackPreconditioner.py`**: This reductor does not reduce the size of the system to be solved but acts as a preconditioner. It builds a scaling matrix to set the displacement vector to 1 up to a certain cut-off.
- **`AllgowerPreconditioner.py`**: This reductor, like the previous, does not reduce the system size but serves as a preconditioner. It uses the QR decomposition of the Jacobian at the predicted point to compute a scaling matrix that preconditions the problem (see [[2]](#2)).
- **`GlobalHarmonicReductor.py`**: Reduces the system size by cutting off harmonics based on a criterion described by C. Gastaldi (2017). It retains only the necessary number of harmonics based on an analysis of the cross-harmonic Jacobian block.
- **`LocalHarmonicReductor.py`**: A subclass of **GlobalHarmonicReductor** that reduces the system's size by cutting harmonics based on C. Gastaldi's criterion (2017). This reductor is local, meaning it cuts harmonic numbers per degree of freedom instead of a global selection as done by the **GlobalHarmonicReductor**.
- **`NLdofsReductor.py`**: Reduces the system's size by eliminating the linear part from the system to be solved, with the linear part being solved at each iteration using a specific linear solver.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Reductors.html).