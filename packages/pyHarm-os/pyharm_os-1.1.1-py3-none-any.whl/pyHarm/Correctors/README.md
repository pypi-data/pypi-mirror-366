# Corrector package presentation

This module contains all the correctors type that are provided by **pyHarm**. The module is organized around an abstract class **ABCCorrector** and a **FactoryCorrector** that is in charge of creating the objects. All analysis object must comply with the **ABCCorrector** abstract class. 

- `ABCAnalysis.py` : The **ABCCorrector** class is an abstract class defining the essential components of any corrector. T
- `FactoryCorrector.py` : This file contains the dictionary of all the correctors that are available as well as the function `generateCorrector` that creates the corrector object based on the desired type of corrector.
- `CorrectorNoContinuation.py` : This corrector corresponds to a fix frequency closure equation.
- `CorrectorPseudoArcLength.py` : This corrector forces the seeked solution to belong to an hyperplan perpendicular to the prediction direction. This corrector allows for treating turning points.
- `CorrectorArcLength.py` : This corrector forces the seeked solution to belong to an hypersphere of radius $`ds`$, where $`ds`$ is the length of the prediction vector. This corrector also allows for treating turning points.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Correctors.html).
