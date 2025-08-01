# DLFTElements subpackage

This subpackage implements a formulation of element that differs from the classical elements using Dynamic Lagrangian Frequency Time method. It is composed of the following modules : 
- `DLFTElement.py` : The DLFT method is a penalisation method for handling constraints. The **DLFTElement** is a modification of the **NodeToNodeElement** that complies with DLFT method peculiarities (thus remaining an abstract class). For a better understanding of DLFT method and its use see. All the **NodeToNodeElement** that uses DLFT must inherit from **DLFTElement** implementation as their residual value depends on the residual of the linear part of the system.
- `DLFTUniGap.py` : This **DLFTElement** is the implementation of **PenaltyUnilateralGap** element using DLFT method. 
- `DLFTFriction.py` : This **DLFTElement** is the implementation of **Jenkins** element using DLFT method.
- `DLFT3D.py` : This **DLFTElement** is the implementation of **Penalty3D** element using DLFT method. It is an assembly of **DLFTUniGap** and **DLFTFriction** residual and jacobian.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/NodeToNodeElements_DLFTElements.html).

