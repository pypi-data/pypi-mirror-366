# aiSSEMBLE Universal Config Loader
aiSSEMBLE Universal Config Loader uses Krausening to provide features to read the configuration from property file and load the configuration to environment variables or to global variables. For the notebook user, it also providers a helper class to extract their notebooks global variables into the property file to set up the configuration for the first time.

## Getting Started

### Notebook User
For the notebook user, to have an easy start, config helper provides a feature to extract the `string` type or `int` type global variables into the configuration property file. The configuration file will be created if it doesn't exist.


#### Example of Extract variables to the property file

The Following example shows how a notebook user can extract the variables from a cell to the property file
```python
# a notebook cell
import os

# variables
test_var1="value_1"
test_var2="value_2"
test_var3="value_3"
test_var4=[1, 2, 3]  # the list variable will not be extracted to property file
test_var5={"a":"b", "c":"d"} # the dict variable will not be extract to property file
os.environ['PROJECT_ID'] = "test-final"
os.environ['ISSUE_ID']="1"

# install the aissemble-universal-config-loader module 
!pip install aissemble-universal-config-loader

# register the `aissemble_universal_config_loader.ipython.config_helper` ipython extension
%load_ext aissemble_universal_config_loader.ipython.config_helper

#extract the `int` type or `string` type global variables to the configuration file
%extract_vars_to_property_file

```

###### Output
After run above cell, expect the next steps printed in the cell output:

The next step contains:
1. The function to load property values as global variables
2. The configuration file location and what variables have been saved
```shell
****************************************************************************************
 Next Steps:
****************************************************************************************
 1: Required
----------------------------------------------------------------------------------------
 To load property values as global variables, add the below code snippets to a new cell and run the cell:

"""
# import the ConfigLoader module
from aissemble_universal_config_loader.config_loader import ConfigLoader

# set configuration file directory, this is for bootstrapping the library
os.environ['KRAUSENING_BASE'] = '/path-to-project-directory/configurations/base'

# load property values as global variables
ConfigLoader().load_as_global()
"""

 Note: Use `ConfigLoader().load_as_env()` to load property values as environment variable.


----------------------------------------------------------------------------------------
 2: Optional
----------------------------------------------------------------------------------------
 The variables have been extracted to /Users/csun/bah/tests/aissemble-lite-test/test-4306-3/backend/configurations/base/configuration.properties.
 You can remove the following variables from your notebook and load them via the ConfigLoader:
 ['test_var1=value_1', 'test_var2=value_2', 'test_var3=value_3']
```

###### Property file
If there is no existing property file, by default, the `configuration.properties` will be generated at the *.ipynb file's sibling directory `configurations/base` with the below content
```properties
test_var1=value_1
test_var2=value_2
test_var3=value_3
```

### Python Project User
#### Installation
Add the `aissemble-universal-config-loader` package to your project

#### Load Property
To load the property, ensure the `configuration.properties` file is already generated. The loader uses Krausening to read properties from a properties file into either global variables or environment variables. The default Krausening base location is `configurations/base` and the default properties file is `configuration.properties`


#### Add `import` Statement

```python
from aissemble_universal_config_loader.config_loader import ConfigLoader
```

#### Set [Krausening_Base]() environment variable
Krausening is useful for defining different configurations per execution environment. For simple local usage, you can simply set `KRAUSENING_BASE` to the directory that contains your configuration file(s). For more detail: https://github.com/TechnologyBrewery/krausening/tree/dev/krausening#krausening-in-one-pint-learn-krausening-in-2-minutes
```python
os.environ['KRAUSENING_BASE']="path-to-property-directory"
```

#### Load Property to _Global Variables_
```python
 ConfigLoader().load_as_global()
```
#### Load Property to _Environment Variables_
```python
 ConfigLoader().load_as_env()
```