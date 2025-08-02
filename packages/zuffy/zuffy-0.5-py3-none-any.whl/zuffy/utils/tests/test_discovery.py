# Authors: scikit-learn-contrib developers
# License: BSD 3 clause

import pytest

from zuffy.utils.discovery import all_displays, all_estimators, all_functions


def test_all_estimators():
    estimators = all_estimators()
    print('Estimator List:', estimators)
    assert len(estimators) == 8

    estimators = all_estimators(type_filter="classifier")
    assert len(estimators) == 2

    estimators = all_estimators(type_filter=["classifier", "transformer"])
    assert len(estimators) == 6

    err_msg = "Parameter type_filter must be"
    with pytest.raises(ValueError, match=err_msg):
        all_estimators(type_filter="xxxx")


def test_all_displays():
    displays = all_displays()
    assert len(displays) == 0


def test_all_functions():
    functions = all_functions()
    print('Function List',functions)
    assert len(functions) == 13
