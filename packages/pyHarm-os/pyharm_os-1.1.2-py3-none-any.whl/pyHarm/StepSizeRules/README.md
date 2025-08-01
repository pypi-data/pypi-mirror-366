# Package StepSizeRules

This package contains all the step size rule types provided by **pyHarm**. It is organized around an abstract class, **ABCStepSizeRule**, and a **FactoryStepSize** responsible for creating the objects. All step size rule objects must adhere to the **ABCStepSizeRule** abstract class. Below is a brief description of each module contained in this subpackage:

- **`ABCStepSizeRule.py`**: The **ABCStepSizeRule** class is an abstract class defining the essential components of any step size rule. One abstract method is defined.
- **`FactoryStepSize.py`**: Contains the dictionary of all available step size rules and the `generateStepSizeRule` function, which creates the **ABCStepSizeRule** object based on the desired corrector type.
- **`StepSizeConstant.py`**: Maintains a constant step size. It is important to use a stop criterion that is compatible with this step size rule.
- **`StepSizeAcceptance.py`**: Adjusts the step size based on the success of previous solutions. The step size is halved if the previous solution was not accepted, or doubled after a set number of consecutive successful solver results (default is 5). The step size is constrained within defined bounds before being returned.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/StepSizeRules.html).