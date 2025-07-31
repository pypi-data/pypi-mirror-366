# pySWATPlus


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14889319.svg)](https://doi.org/10.5281/zenodo.14889319)


`pySWATPlus` is an open-source Python package developed and maintained by [ICRA](https://icra.cat/).
It provides a programmatic interface to the SWAT+ model, allowing users to run simulations, modify input files, and streamline custom experimentation through the model’s `TxtInOut` folder.


## ✨ Key Features

- Navigate and read files in the SWAT+ `TxtInOut` folder.
- Modify input parameters and save the updated files.
- Run SWAT+ simulations either in the main `TxtInOut` folder or in a user-specified directory.
- Perform sensitivity analysis on model parameters using [SALib](https://github.com/SALib/SALib), with support for parallel computation.



## 📥 Install pySWATPlus

To install from PyPI repository:

```bash
pip install pySWATPlus
```

To install the latest development version from GitHub:

```bash
pip install git+https://github.com/swat-model/pySWATPlus.git
```

To install from source in editable mode within your desired `conda` environment:

```bash
# Activate your Conda environment
conda activate <environment_name>

# Install required tools and clone the repository
pip install build
cd C:\Users\Username\Folder  # Replace with your actual path
git clone https://github.com/swat-model/pySWATPlus.git
cd pySWATPlus

# Build the package
python -m build

# Install in editable mode
pip install --editable .
```

## 🚀 Quickstart
A brief example of how to start:

```python
import pySWATPlus
txtinout = pySWATPlus.TxtinoutReader(
    path=r"C:\Users\Username\TxtInOut" # Replace with your actual path
)
```

## 📚 Documentation

For a guide to setting up first SWAT+ project and other functionalities with examples,
refere to the [pySWATPlus documentation](https://pyswatplus.readthedocs.io/en/latest/).



## 📖 Citation
If you use **pySWATPlus** in your research or project, please cite the **specific version** you used. For general citation of the project (which always points to the latest version), use the **concept DOI** provided below.

---

### 🔹 Citing a Specific Version

Each release of pySWATPlus is archived on [Zenodo](https://zenodo.org/) with its own DOI. To cite a specific version:

1. Visit the Zenodo project page: [https://doi.org/10.5281/zenodo.14889319](https://doi.org/10.5281/zenodo.14889319)
2. Under **Versions**, click the release you used (e.g., `v1.0.1`)
3. Copy the citation format provided there (BibTeX, APA, etc.)

### 🔹 Citing the Latest Version (Concept DOI)

To cite the most recent version (not tied to a specific release):

```bibtex
@software{joan_salo_pyswatplus_latest,
  author       = {Joan Saló and
                  Debasish Pal and
                  Oliu Llorente},
  title        = {swat-model/pySWATPlus},
  year         = 2025,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.14889319},
  url          = {https://doi.org/10.5281/zenodo.14889319},
  note         = {This DOI always points to the latest version of pySWATPlus.},
}
```