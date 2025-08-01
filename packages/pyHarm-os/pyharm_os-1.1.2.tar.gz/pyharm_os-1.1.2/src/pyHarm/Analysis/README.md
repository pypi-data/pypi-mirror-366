# Analysis Package Presentation

This package encompasses all the types of analyses offered by **pyHarm**. The package is centered around an abstract class, **ABCAnalysis**, and a **Factory** responsible for creating the objects. Every analysis object must adhere to the **ABCAnalysis** abstract class.

- **`ABCAnalysis.py`**: Defines the abstract class governing the critical components of any analysis.
- **`FactoryNonLinearStudy.py`**: This file contains the dictionary of all available analyses, as well as the `generateNonLinearAnalysis` function, which creates analysis objects based on the type of analysis and the provided input.
- **`FRF_NonLinear.py`**: Nonlinear forced response analysis over a range of frequencies, utilizing a prediction/correction procedure.
- **`Linear_Analysis.py`**: Linear forced response analysis over a range of frequencies, employing modal superposition.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Analysis.html).