# PyPSA-Xplore
 
The purpose of this repository is to develop Jupyter notebooks for step-by-step analysis of results obtained with PyPSA-*something* (PyPSA-Spain, PyPSA-Eur, etc.).


## How to use PyPSA-Xplore:



1. **Clone the repository**:

    ```bash
    git clone https://github.com/cristobal-GC/pypsa-Xplore
    ```

    or download it as a [ZIP file](https://github.com/cristobal-GC/pypsa-Xplore/archive/refs/heads/main.zip).


2. **Open the `params.yaml` file** and set the path to your PyPSA-*something* directory in the first field, **`rootpath:`**.

3. **Run the Jupyter notebooks** located in the different folders:

    - Folder `Xplore_rules` contains notebooks associated with some of the rules included in the workflow (one notebook per rule, with the same name). You only need to complete the first section of the notebook, named `parameters`, using the same values you used in the related config file of the PyPSA-*something* model. Then, for earh specific plot, there may be some extra parameter section to select among different options.

    - Folder `Xplore_data_ES` contains notebooks with analyses of the specific data for Spain (relevant only for PyPSA-Spain).

    - Folder `functions` contains auxiliary functions. You may want to explore them if you're interested in understanding or improving how specific functionalities are implemented, though it's not required for a basic use of **PyPSA-Xplore**.








