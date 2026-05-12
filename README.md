# PyPSA-*X*plore

**PyPSA-*X*plore** is a collection of Jupyter notebooks for exploring and visualizing results from **PyPSA-*X*** models (e.g., *PyPSA-Spain*, *PyPSA-Eur*).


## Installation

Clone the repository:

```bash
git clone https://github.com/cristobal-GC/pypsa-Xplore
```

or [download the ZIP file](https://github.com/cristobal-GC/pypsa-Xplore/archive/refs/heads/main.zip) and extract it locally.


## Usage

1. Open [`params.yaml`](params.yaml) and set the path to your PyPSA-*X* model:

   ```yaml
   rootpath: /path/to/your/PyPSA-X/model/
   ```

2. Open any notebook and run it. Using the same Python environment as your PyPSA-*X* model is recommended.


## Repository Structure

```
pypsa-Xplore/
│
├── Xplore_rules/              # Notebooks for main workflow rules (network building process)
├── Xplore_rules_heating/      # Notebooks for heating sector rules
├── Xplore_rules_sectors/      # Notebooks for multi-sector rules
├── Xplore_rules_transport/    # Notebooks for transport sector rules
├── Xplore_rules_shipping/     # Notebooks for shipping sector rules
├── Xplore_rules_biomass/      # Notebooks for biomass sector rules
├── Xplore_rules_industry/     # Notebooks for industry sector rules
├── Xplore_data/               # Notebooks for data from PyPSA-Eur
├── Xplore_data_ES/            # Notebooks for data from PyPSA-Spain
│
├── functions/                 # Helper functions for data processing and visualization
│
└── params.yaml                # General parameters for PyPSA-Xplore
```

Each notebook in `Xplore_rules*/` corresponds to a rule from the model workflow. Fill in the `parameters` section with the values from your PyPSA-*X* configuration file.


## Contributing

Contributions are welcome!
If you’d like to improve or extend **PyPSA-*X*plore**, feel free to:
- Open an issue to report a bug or suggest an enhancement.
- Submit a pull request with your proposed changes.

## License

This project is licensed under the [MIT License](LICENSE) — feel free to use and modify it for your own research or projects.

