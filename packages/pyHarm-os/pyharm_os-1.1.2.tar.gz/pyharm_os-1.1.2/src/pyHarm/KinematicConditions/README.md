# Package KinematicConditions

This package contains all the types of kinematic conditions provided by **pyHarm**. It is organized around an abstract class, **ABCKinematic**, and a **FactoryKinematic** that is responsible for creating the objects. All kinematic condition objects must adhere to the **ABCKinematic** abstract class. The package contains the following modules:

- **`ABCKinematic.py`**: The **ABCKinematic** class is an abstract class defining the essential components of any kinematic condition.
- **`FactoryKinematic.py`**: Contains the dictionary of all available kinematic conditions and the `generateKinematic` function, which creates the kinematic condition object based on the type of solver desired.
- **`GODisplacement.py`**: Imposes a displacement of the form \(\displaystyle x = \frac{amp}{\omega^{dto}} \cdot l\).
- **`AccelImposed.py`**: A subclass of `GODisplacement` with `dto`=2, imposing acceleration on a given degree of freedom (dof).
- **`SpeedImposed.py`**: A subclass of `GODisplacement` with `dto`=1, imposing speed on a given dof.
- **`DispImposed.py`**: A subclass of `GODisplacement` with `dto`=0, imposing displacement on a given dof.
- **`BaseProjection.py`**: Imposes a base projection between a master substructure and a slave substructure through a transformation matrix. The residual of the slave substructure is projected back onto the master substructure.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/KinematicConditions.html).