# PyPSA-Xplore
 
The purpose of this repository is to develop Jupyter notebooks for step-by-step analysis of results obtained with PyPSA-*something* (PyPSA-Spain, PyPSA-Eur, etc.).


## How to use PyPSA-Xplore:



1. **Clone the repository**:

    ```bash
    git clone https://github.com/cristobal-GC/pypsa-Xplore
    ```

    or download it as a [ZIP file](https://github.com/cristobal-GC/pypsa-Xplore/archive/refs/heads/main.zip).


2. **Open the `params.yaml` file** and set the path to your PyPSA-*something* directory in the first field, **`rootpath:`**.

3. **Run the Jupyter notebooks** located in the `Xplore_rules` folder.  
   Each notebook contains analyses for the outputs of the rule with the same name as the notebook.  
   You only need to complete the first section, named `parameters`, using the same values you used in the config file of the PyPSA-*something* model that generated the outputs for the rule in question.



## Comments:


- Notebooks in the `Xplore_scenarios` and `Xplore_sets` folders are currently under development.

- The `functions` folder contains auxiliary functions. You may want to explore them if you're interested in understanding or improving how specific functionalities are implemented, though it's not required for basic use.







