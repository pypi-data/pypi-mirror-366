def test_setVSFlags(rpm):
    ts = rpm.TransactionSet()

    # setVSFlags returns the previous value.
    # As we do not know what the initial value was, we don't check the result
    # here.
    ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)

    # However we know the next call should return what we set above.
    assert ts.setVSFlags(rpm._RPMVSF_NODIGESTS) == rpm._RPMVSF_NOSIGNATURES


def test_setKeyring(rpm):
    ts = rpm.TransactionSet()

    # Can setKeyring to an empty keyring without crashing.
    ts.setKeyring(rpm.keyring())

    # Can setKeyring to None without crashing.
    ts.setKeyring(None)


def test_initial_flags(rpm_native, rpm_dyn):
    # Initial value of flags should be same on both implementations
    ts_native = rpm_native.TransactionSet()
    ts_dyn = rpm_dyn.TransactionSet()

    assert ts_native.getVSFlags() == ts_dyn.getVSFlags()
