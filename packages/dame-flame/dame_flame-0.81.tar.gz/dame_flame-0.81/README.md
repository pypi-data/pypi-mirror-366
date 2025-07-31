
[![Build Status](https://app.travis-ci.com/almost-matching-exactly/DAME-FLAME-Python-Package.svg?branch=master)](https://app.travis-ci.com/almost-matching-exactly/DAME-FLAME-Python-Package)
[![Coverage Status](https://coveralls.io/repos/github/almost-matching-exactly/DAME-FLAME-Python-Package/badge.svg)](https://coveralls.io/github/almost-matching-exactly/DAME-FLAME-Python-Package)

<!-- Comment hi.  -->
# DAME-FLAME
A Python package for performing matching for observational causal inference on datasets containing discrete covariates
--------------------------------------------------

## Documentation [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/)

DAME-FLAME is a Python package for performing matching for observational causal inference on datasets containing discrete covariates. It implements the Dynamic Almost Matching Exactly (DAME) and Fast, Large-Scale Almost Matching Exactly (FLAME) algorithms, which match treatment and control units on subsets of the covariates. The resulting matched groups are interpretable, because the matches are made on covariates, and high-quality, because machine learning is used to determine which covariates are important to match on.

### Installation

#### Dependencies
`dame-flame` requires Python version (>=3.6). Install from [here](https://www.python.org/downloads/) if needed.

- pandas>=0.11.0
- numpy>= 1.16.5
- scikit-learn>=0.23.2


If your python version does not have these packages, install from [here](https://packaging.python.org/tutorials/installing-packages/).

To run the examples in the examples folder (these are not part of the package), Jupyter Notebooks or Jupyter Lab (available [here](https://jupyter.org/install)) and Matplotlib (>=2.0.0) is also required.

#### User Installation

Download from PyPi via
$ pip install dame-flame

#### Source Code
The source code repository, featuring tests, and an issue tracker is [here](https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package)

#### Citation

If you use dame-flame in a scientific publication, we would appreciate citations:

Neha R. Gupta, Vittorio Orlandi, Chia-Rui Chang, Tianyu Wang, Marco Morucci, Pritam Dey, Thomas J. Howell, Xian Sun, Angikar Ghosal, Sudeepa Roy, Cynthia Rudin, Alexander Volfovsky (2025). dame-flame: A Python Package Providing Fast Interpretable Matching for Causal Inference. Journal of Statistical Software, 113(2), 1-26. https://doi.org/10.18637/jss.v113.i02