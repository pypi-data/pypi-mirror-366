import os
import base64

import pytest


def long_type(x):
    try:
        # py2
        return long(x)
    except:
        return x


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
WALRUS_RPM = os.path.join(DATA_DIR, "walrus-5.21-1.noarch.rpm")
TEST_SRPM = os.path.join(DATA_DIR, "test-srpm01-1.0-1.src.rpm")


# Some expected values which are too large to put inline
WALRUS_RSAHEADER = base64.b64decode(
    b"iQEVAwUAT2Iike+FzOP3j7GVAQKeawgAn5r7157FaTinf7xEyoGK6ct7XJ5w7yAS3QYtgpH0XGEP"
    b"P+mBO9PBC/8Dq1VCo7tdq7Vd16tRA92e2RiqMXQFaWo4a5grLMZFzSIOcBHyV/RZi1pc7IuYVBAS"
    b"l9D5Wn/OBYrx3z6ju76+vB4RCBrxZ7KW6myaQu3i7EqJ97eoks/ew/apta6WX4GgDIydzMn8gsoY"
    b"vdmHqiJ1YVItcmn7/DPYzChaE7EwUGANNbd+y7waCpVIxpf5c8oPv85Yth103sRXv5BdUIkXW6IA"
    b"J72i/US/40M24yOAPJz9mvx0PjKAfEvg1krlE0pcIP94tFFZE5Xr0jEfI85v0GLEa9hmoA=="
)


def get_header(rpm, filename):
    ts = rpm.TransactionSet()
    ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES | rpm._RPMVSF_NODIGESTS)

    with open(filename, "rb") as f:
        hdr = ts.hdrFromFdno(f.fileno())

    return hdr


@pytest.fixture
def header_walrus(rpm):
    yield get_header(rpm, WALRUS_RPM)


@pytest.fixture
def header_test_srpm(rpm):
    yield get_header(rpm, TEST_SRPM)


@pytest.mark.parametrize(
    "rpmname,key,value",
    [
        ("walrus", "name", u"walrus"),
        ("walrus", "dsaheader", None),
        ("walrus", "rsaheader", WALRUS_RSAHEADER),
        ("walrus", "sourcepackage", None),
        ("test_srpm", "sourcepackage", long_type(1)),
        ("walrus", "requireversion", [u"3.0.4-1", u"4.0-1"]),
        ("walrus", "requireflags", [long_type(16777290), long_type(16777290)]),
        ("test_srpm", "provideflags", []),
        ("walrus", "filestates", []),
        ("walrus", "summary", u"A dummy package of walrus"),
        ("test_srpm", "filestates", []),
    ],
)
def test_header_value(request, rpmname, key, value, rpm):
    hdr = request.getfixturevalue("header_" + rpmname)

    key = getattr(rpm, "RPMTAG_%s" % key.upper())

    actual_value = hdr[key]

    assert value == actual_value
    assert type(value) == type(actual_value)
