# Package Substructures

This package contains all the substructure types provided by **pyHarm**. It is organized around an abstract class, **ABCSubstructure**, and a **FactorySubstructure** responsible for instantiating the objects. All system objects must adhere to the **ABCSubstructure** abstract class. The main purpose of **ABCSubstructure**-based classes is to generate a DataFrame and create the degrees of freedom. Additionally, these classes can generate a dictionary that describes connectors or kinematic conditions to add to the **ABCSystem**. Some descriptions of the provided modules in this package are given below:

- **`ABCSubstructure.py`**: The **ABCSubstructure** class is an abstract class defining the essential components of any substructure. Two abstract methods are mandatory.
- **`OnlyDofs.py`**: The `OnlyDofs` class is designed to create degrees of freedom (dofs) within the system but does not generate any new connectors or kinematic conditions.
- **`Substructure.py`**: The `Substructure` class is the primary class in pyHarm for creating dofs and adding a `Substructure` element to the system. The `Substructure` requires the matrices `M`, `G`, `C`, `K` to be defined, as well as the number of dofs per node (`ndofs`). Other characteristics can be inferred. When using super-elements, the number of modes (`nmodes`) must be provided. It is assumed that the modal nodes are positioned last in the matrices.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Substructures.html).