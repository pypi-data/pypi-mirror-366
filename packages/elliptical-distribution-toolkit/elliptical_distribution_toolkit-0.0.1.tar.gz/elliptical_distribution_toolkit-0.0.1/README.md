<img src="https://gitlab.com/elliptical-distribution-toolkit-dev/elliptical-distribution-toolkit/raw/main/images/elliptical-tile-logo.1500px.png" alt="elliptical-logo" height="150"> 


# Elliptical-Distribution Toolkit

[![pipeline status](https://gitlab.com/elliptical-distribution-toolkit-dev/elliptical-distribution-toolkit/badges/main/pipeline.svg)](https://gitlab.com/elliptical-distribution-toolkit-dev/elliptical-distribution-toolkit/pipelines)
[![coverage report](https://gitlab.com/elliptical-distribution-toolkit-dev/elliptical-distribution-toolkit/badges/main/coverage.svg)](https://gitlab.com/elliptical-distribution-toolkit-dev/elliptical-distribution-toolkit/commits/main)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://gitlab.com/elliptical-distribution-toolkit-dev/elliptical-distribution-toolkit/blob/main/LICENSE)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![python versions](https://img.shields.io/badge/py-%3E%3D3.7-blue)](https://pypi.python.org/pypi/elliptical-distribution-toolkit)
[![numpy versions](https://img.shields.io/badge/numpy-%3E%3D1.23-blue)](https://www.numpy.org/)
[![pypi version](https://img.shields.io/pypi/v/elliptical-distribution-toolkit.svg)](https://pypi.python.org/pypi/elliptical-distribution-toolkit)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/elliptical-distribution-toolkit.svg)](https://anaconda.org/conda-forge/elliptical-distribution-toolkit)


## Overview

This package, `elliptical-distribution-toolkit`, provides a variety of functions that deal with multivariate elliptical distributions. Two key distributions are the multivariate (mv) Gaussian and mv Student-t. 

Among the provided functions, `mahal_explicit` and `mahal_estimate` resolve longstanding issues with other implementations of the Mahalanobis distance calculation wherein the latter do not properly handle vectorized input whereas the implementations in this package do. 


## Package Installation

The two package hosts for `elliptical-distribution-toolkit` are [PyPi]() and [Conda-Forge](). The packages are identical and the only difference is the means of delivery. From PyPi, use `pip`,

```bash
$ pip install elliptical-distribution-toolkit
```

and from Conda-Forge use `conda`:

```bash
$ conda install -c conda-forge elliptical-distribution-toolkit
```

Once installed, the package is importable to Python:

```python
>>> import elliptical_distribution_toolkit as ell_tk
```

## Package Dependency

The only dependencies `elliptical-distribution-toolkit` has at this time is on [python >= 3.7](https://www.python.org/) and [numpy >= 1.23](https://www.numpy.org/). 


## Buell Lane Press

[Buell Lane Press](https://buell-lane-press.co) is the package sponsor. 

