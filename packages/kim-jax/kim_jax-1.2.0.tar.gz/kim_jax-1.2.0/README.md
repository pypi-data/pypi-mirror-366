# Knowledge-Informed Mapping (KIM) Toolkit

<figure>
  <img src="./docs/figures/Figure-KIM.png" alt="">
</figure>

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Documentation](#documentation)
- [Examples](#examples)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [How to Cite](#how-to-cite)
- [Contacts](#contacts)

## Overview
KIM is a Knowledge-Informed Mapping toolkit in Python to optimize the development of the mapping $ƒ$ from a vector of inputs $\mathbf{X}$ to a vector of outputs $\mathbf{Y}$. KIM mainly builds on the methodology development of deep learning-based inverse mapping in [Jiang et al. 2023](https://hess.copernicus.org/articles/27/2621/2023/hess-27-2621-2023.html) and [Wang et al. 2025](TBD). It involves two key procedures: (1) an exploratory data analysis using information theory to identify the dependency between $\mathbf{X}$ and $\mathbf{Y}$ and filter out both insignificant and redundant inputs through global sensitivity analysis and conditional independence testing; and (2) ensemble learning of $ƒ$ using neural networks to account for its structural uncertainty. KIM is mostly rewritten in [JAX](https://github.com/jax-ml/jax) and also supports basic parallel computing on CPU cores for statistical significance test and ensemble learning by using [Joblib](https://joblib.readthedocs.io/en/stable/).

## Installation
1. [Install Miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/) if you don't have it already.

2. Open a terminal and create a new virtual environment named `kim` with Python 3.11:
   ```bash
   conda create --name kim python=3.11
   ```

3. Activate the newly created virtual environment:
   ```bash
   conda activate kim
   ```

4. Install Turboflow using pip within the activated virtual environment:
   ```bash
   pip install kim-jax
   ```

5. (Optional) Download the git repo to get the example jupyter notebooks:
    ```bash
    git clone https://github.com/PeishiJiang/KIM.git
    ```

## Documentation
<!-- Please refer to [the Approach](./doc/math.md) for a complete description of the mathematical method. -->
The official documentation is hosted on [the package website](TBD). Please refer to [Math behind KIM](TBD) for a complete description of the theory behind the package.

## Examples
We provide one tutorial case and two real cases of applying KIM to performing inverse modeling by using Jupyter notebook to illustrate the package usage.

**Case 0: [Emulating a multivariate nonlinear system](./examples/tutorial/).** We develop forward mappings to emulate three predictand driven by four predictors via a nonlinear system.

**Case 1: [Calibrating a cloud chamber model](./examples/im_cloudmodel/).** We develop inverse mappings to estimate two key parameters, i.e., wall fluxes ($\lambda_w$) and collision processes ($\lambda_c$) of a cloud chamber model from synthetic observations.

**Case 2: [Calibrating an integrated hydrological model](./examples/im_ats/).** We develop inverse mappings to estimate eight parameters of the Advanced Terrestrial Simulator (ATS) from the streamflow observations at the outlet of Coal Creek watershed, CO, USA.

## License
Distributed under the Simplified BSD License. See [LICENSE](./LICENSE) for more information.

## Acknowledgements
This work was funded by the Laboratory Directed Research and Development Program at Pacific Northwest National Laboratory. 

## How to Cite
The repository is under review. We will provide a complete citation upon the acceptance of the repo/paper.

## Contacts
Peishi Jiang (shixijps@gmail.com)

<hr>

[Go to Top](#table-of-contents)