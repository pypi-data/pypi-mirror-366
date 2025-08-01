# NodeToNodeElements Package

The `NodeToNodeElements` subpackage provides implementations of `ABCElement` that allow for connecting two nodes. This package is composed of the following modules:

- **`NodeToNodeElement.py`**: The `NodeToNodeElement` class is the abstract class governing the definition of an element affecting two nodes of the system. This abstract class inherits from `ABCElement` and implements some abstract methods responsible for creating indices of interest and properly reading the input dictionary.
- **`GeneralOrderElement.py`**: A general order element that acts as a polynomial element at a fixed time order.
- **`LinearSpring.py`**: Inherits from the **GeneralOrderElement** class, representing a linear spring.
- **`LinearDamper.py`**: Inherits from the **GeneralOrderElement** class, representing a dashpot.
- **`CubicSpring.py`**: Inherits from the **GeneralOrderElement** class, representing a cubic spring.
- **`GeneralOrderForcing.py`**: An element used to create forcing that does not depend on the displacement vector. Harmonic loading must be given in the form of the `ho` parameter, along with a phase lag `phi`, to create a loading unitary vector on the right degrees of freedom. The order of derivative `dto` allows for loading with a polynomial dependence in \(\omega\), while the parameter `amp` drives the amplitude.
- **`CosinusForcing.py`**: A **GeneralOrderForcing** element that imposes `dto`=0, `ho`=1, and `phi`=0, corresponding to a first harmonic cosine forcing.
- **`SinusForcing.py`**: A **GeneralOrderForcing** element that imposes `dto`=0, `ho`=1, and `phi`=\(\frac{\pi}{2}\), corresponding to a first harmonic sine forcing.
- **`PenaltyUnilateralGap.py`**: Represents a gap that adds rigidity to the connection when the gap is closed, in the form of a linear spring. This gap closes on a single side, meaning the sign of the displacement is important.
- **`PenaltyBilateralGap.py`**: Represents a gap that adds rigidity to the connection when the gap is closed, in the form of a linear spring. This gap closes when the norm of the displacement equals the gap value, allowing closure in multiple directions on both sides.
- **`Jenkins.py`**: An implementation of the classical Jenkins element for modeling dry friction using Coulomb's laws. As friction is a hysteretic phenomenon, a correction loop is present in the residual computation to account for hysteretic loops.
- **`Penalty3D.py`**: An implementation of the classical friction contact element that allows contact separation. It is implemented using an assembly of **Jenkins** and **PenaltyUnilateralGap** residual and Jacobian functions.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/NodeToNodeElements.html).