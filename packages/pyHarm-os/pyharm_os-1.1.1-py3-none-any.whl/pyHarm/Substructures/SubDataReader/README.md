# Package SubDataReader

This package contains all the substructure data reader types provided by **pyHarm**. It is organized around an abstract class, **ABCReader**, and a **FactoryReader** responsible for instantiating the objects. All system objects must adhere to the **ABCReader** abstract class. A brief description of the modules included in the package is provided below:

- **`ABCReader.py`**: The **ABCReader** class is an abstract class defining the essential components of any substructure. One abstract method is defined.
- **`FactoryReader.py`**: Contains the dictionary `SubstructureReaderDictionary` of all available stop criteria and the `generate_subreader` function, which creates the reader object based on the selected keyword.
- **`GenericReader.py`**: The basic reader provided by pyHarm. It can read input data where matrices are provided under the `matrix` key of the input dictionary, as well as read `.mat` files using `scipy.io.loadmat` with certain formatting, and `.h5` files. All tutorials in pyHarm use this generic reader. If the `reader` key is not provided in the substructure description, this reader serves as the default.

For a detailed description of these modules, [**click here**](https://pyharm-saf.readthedocs.io/en/latest/Substructures_DataReader.html).