# Package Predictors

This package contains all the predictor types provided by **pyHarm**. It is organized around an abstract class, **ABCPredictor**, and a **FactoryPredictor** that is responsible for creating the objects. All predictor objects must adhere to the **ABCPredictor** abstract class. Below is a brief description of each module:

- **`ABCPredictor.py`**: The **ABCPredictor** class is an abstract class defining the essential components of any nonlinear solver. One abstract method is defined.
- **`FactoryPredictor.py`**: Contains the dictionary of all available predictors and the `generatePredictor` function, which creates the predictor object.
- **`PredictorPreviousSolution.py`**: Predicts the next point using the same displacement as the last converged point, stepping onto the angular frequency only.
- **`PredictorTangent.py`**: Uses the Jacobian at the last converged point to compute the tangent of the Jacobian based on a QR decomposition.
- **`PredictorSecant.py`**: Inherits from the tangent predictor to make the first point prediction. Otherwise, it uses the last two converged points to compute the secant line and predict the next point based on the required step size.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Predictors.html).