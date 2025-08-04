import pytest


@pytest.mark.parametrize(
    "evr1,evr2,result",
    [
        [("0", "0", "0"), ("1", "1", "1"), -1],
        [("2", "0", "0"), ("1", "1", "1"), 1],
        [("", "0", "0"), ("", "1", "1"), -1],
    ],
)
def test_labelCompare(rpm, evr1, evr2, result):
    assert rpm.labelCompare(evr1, evr2) == result


@pytest.mark.parametrize(
    "evr1,evr2",
    [
        [("0", "0", "0"), (None, None, None)],
    ],
)
def test_labelCompare_errors(rpm, evr1, evr2):
    with pytest.raises(ValueError) as excinfo:
        rpm.labelCompare(evr1, evr2)

    assert "invalid version" in str(excinfo.value)
