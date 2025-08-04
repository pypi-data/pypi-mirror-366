import os

MISSING = object()
try:
    import rpm as native
except:
    native = MISSING

import pytest

from rpmdyn import _rpm as dyn


def check_missing(x):
    if x is MISSING:
        msg = "native rpm bindings not available"
        if os.environ.get("ALLOW_MISSING_NATIVE") == "1":
            pytest.skip(msg)
        raise AssertionError(msg)
    return x


@pytest.fixture(params=[native, dyn], ids=["native", "dyn"])
def rpm(request):
    yield check_missing(request.param)


@pytest.fixture()
def rpm_native():
    yield check_missing(native)


@pytest.fixture()
def rpm_dyn():
    yield dyn
