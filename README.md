# PyPSA-*X*plore

**PyPSA-*X*plore** provides a collection of Jupyter notebooks for step-by-step analysis of results obtained with **PyPSA-*X*** models (e.g., *PyPSA-Spain*, *PyPSA-Eur*, etc.).  
It is designed to help users explore, visualize, and understand model outputs in a structured and reproducible way.



## 🧭 Overview

This repository contains:
- Notebooks to explore results based on specific workflow rules.
- Notebooks for Spain data analysis (relevant only for *PyPSA-Spain*).
- Auxiliary Python functions that support data handling and visualization.



## ⚙️ Installation

Clone the repository or download it as a ZIP file:

```bash
git clone https://github.com/cristobal-GC/pypsa-Xplore
```

or [download the ZIP file](https://github.com/cristobal-GC/pypsa-Xplore/archive/refs/heads/main.zip) and extract it locally.




## 🚀 Usage

1. **Set up the path to your PyPSA-*X*** model:

   Open the file [`params.yaml`](params.yaml) and edit the first field:

   ```yaml
   rootpath: /path/to/your/PyPSA/model/
   ```

2. **Run the Jupyter notebooks:**

   Use the same environment you used to run your **PyPSA-*X*** model.

   Then open any notebook from the repository folders (see below).


## 📂 Repository Structure

```
pypsa-Xplore/
│
├── Xplore_rules/        # Notebooks associated with specific PyPSA workflow rules
│                        # (one notebook per rule, with the same name)
│
├── Xplore_data_ES/      # Notebooks for Spain data analysis (relevant only for PyPSA-Spain).
│
├── functions/           # Auxiliary Python functions used in the notebooks
│
├── params.yaml          # File where you define your PyPSA model root path
└── README.md            # This file
```

### Folder details

- **`Xplore_rules/`**  
  Each notebook corresponds to a rule from the PyPSA model workflow.  
  Fill in the **`parameters`** section with the same values used in the configuration file of the PyPSA-*X* model.
  Some notebooks include extra parameter sections for customizing plots.

- **`Xplore_data_ES/`**  
  Contains notebooks for analyzing Spain-specific data (only relevant for *PyPSA-Spain*).

- **`functions/`**  
  Includes helper functions for data processing and visualization.  
  Exploring this folder can be useful if you want to understand or extend **PyPSA-*X*plore**, though it’s not required for basic usage.



## 🤝 Contributing

Contributions are welcome!  
If you’d like to improve or extend **PyPSA-*X*plore**, feel free to:
- Open an issue to report a bug or suggest an enhancement.
- Submit a pull request with your proposed changes.


## 📄 License

This project is licensed under the [MIT License](LICENSE) — feel free to use and modify it for your own research or projects.

