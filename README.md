# PyPSA-*X*plore

**PyPSA-*X*plore** is a collection of Jupyter notebooks for exploring and visualizing results from **PyPSA-*X*** models (e.g., *PyPSA-Spain*, *PyPSA-Eur*).


## Installation

Clone the repository:

```bash
git clone https://github.com/cristobal-GC/pypsa-Xplore
```

or [download the ZIP file](https://github.com/cristobal-GC/pypsa-Xplore/archive/refs/heads/main.zip) and extract it locally.

### Environment (pixi)

The environment is defined with [pixi](https://pixi.sh) in [`pixi.toml`](pixi.toml). From the
root of your clone:

```bash
pixi install                 # create the default environment
pixi run lab                 # launch JupyterLab in that environment
```

If you plan to commit notebooks, use the `dev` environment instead — it also provides
`nbstripout` (see [Notebook setup](#notebook-setup-required-before-committing-ipynb-files)).


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
├── Xplore_networks/           # Unified notebook to analyse the network at any workflow stage
├── Xplore_rules/              # Notebooks for main workflow rules (network building process)
├── Xplore_rules_heating/      # Notebooks for heating sector rules
├── Xplore_rules_transport/    # Notebooks for transport sector rules
├── Xplore_rules_shipping/     # Notebooks for shipping sector rules
├── Xplore_rules_biomass/      # Notebooks for biomass sector rules
├── Xplore_rules_industry/     # Notebooks for industry sector rules
├── Xplore_rules_sectors/      # Notebooks for multi-sector rules
├── Xplore_data/               # Notebooks for data from PyPSA-Eur
├── Xplore_data_ES/            # Notebooks for data from PyPSA-Spain
├── Xplore_csvs/               # Notebooks for csv data resulting from the optimisation in PyPSA-Spain
│
├── functions/                 # Helper functions for data processing and visualization
│
└── params.yaml                # General parameters for PyPSA-Xplore
```

Each notebook in `Xplore_rules*/` corresponds to a rule from the model workflow. Fill in the `parameters` section with the values from your PyPSA-*X* configuration file.

### Unified network notebook

[`Xplore_networks/network.ipynb`](Xplore_networks/network.ipynb) replaces the seven
network-building notebooks in `Xplore_rules/` (`base_network` → `solve_sector_network`) with a
single one. In the *Parameters* cell you choose the `rule` (plus `clusters/opts/sector_opts/horizon`
as needed) and the notebook loads the matching network. Sections are **auto-detected** from the
loaded network, so only the ones that make sense for that state run.

Map boundaries are taken from `params.yaml` (`boundaries_offshore_<spatial_domain>`), selected
with the `spatial_domain` tag (`'ES'`, `'EU'`, ...). It does **not** use NUTS files (no
NUTS-level aggregation maps). The original per-rule notebooks are kept unchanged.


## Contributing

Contributions are welcome!
If you’d like to improve or extend **PyPSA-*X*plore**, feel free to:
- Open an issue to report a bug or suggest an enhancement.
- Submit a pull request with your proposed changes.

### Notebook setup (required before committing `.ipynb` files)

This repository uses [`nbstripout`](https://github.com/kynan/nbstripout) to keep Jupyter notebook outputs and execution metadata out of git history. The `*.ipynb filter=nbstripout` binding is already declared in [`.gitattributes`](.gitattributes), but the filter itself must be installed and activated **in each local clone** — otherwise notebooks will be committed with outputs and pollute the diff.

`nbstripout` is provided by the `dev` [pixi](https://pixi.sh) environment. From the root of your clone, run once:

```bash
pixi install -e dev
pixi run -e dev nbstripout --install   # registers the clean/smudge filter in this clone's .git/config
```

Verify with `pixi run -e dev nbstripout --status`; it should report that nbstripout is installed in this repository. From that point on, every `git commit` of a `.ipynb` file will automatically strip outputs and execution metadata.

If you cloned the repo and made commits *before* activating the filter, re-normalize the affected notebooks:

```bash
git add --renormalize "*.ipynb"
git commit -m "chore: strip notebook outputs"
```

## License

This project is licensed under the [MIT License](LICENSE) — feel free to use and modify it for your own research or projects.

