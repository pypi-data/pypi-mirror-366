# All Relevant Feature Selection Generator Library (ARFS-Gen)
![PyPI](https://img.shields.io/pypi/v/arfs_gen)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/arfs_gen)
![PyPI - License](https://img.shields.io/pypi/l/arfs_gen)

This repository contains a python library to generate synthetic (toy) data for use in research papers when evaluating all relevant feature selection e.g.  used in [fri](https://github.com/lpfann/fri).

It allows creating datasets with a specified number of strongly and weakly relevant features as well as random noise features.

In the newest revision it also includes methods which generate data with privileged information.

It works by utilizing existing methods from `numpy` and `scikit-learn`.
# Install
The library is available on [PyPi](https://pypi.org/project/arfs-gen/).
Install via `pip`:
```shell
pip install arfs_gen
```
or clone this repository and use:
```shell
pip install .
```

# Usage
In the following we generate a simple regression data set with a mix of strongly and weakly relevant features:

```python
    # Import relevant method
    from arfs_gen import genRegressionData
    # Import model
    from sklearn.svm import LinearSVR

    # Specify parameters
    n = 100
    # Features
    strRel = 2
    strWeak = 2
    # Overall number of features (Rest will be filled by random features)
    d = 10

    # Generate the data
    X, y = genRegressionData(
        n_samples=n,
        n_features=d,
        n_redundant=strWeak,
        n_strel=strRel,
        n_repeated=0,
        noise=0,
    )
    # Fit a model
    linsvr = LinearSVR()
    linsvr.fit(X, y)
```

# Development
For dependency management we use the newly released [poetry](https://python-poetry.org/) tool.

If you have `poetry` installed, use
```shell
$ poetry install
```  
inside the project folder to create a new `venv` and to install all dependencies.
To enter the newly created `venv` use 
```shell 
$ poetry env
```
to open a new shell inside.
Or alternatively run commands inside the `venv` with `poetry run ...`.

## Test
Test it by running `poetry run pytest`.
