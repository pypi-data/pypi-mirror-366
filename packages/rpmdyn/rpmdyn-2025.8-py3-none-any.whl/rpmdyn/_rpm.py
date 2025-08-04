from functools import partial

from ._ffi import rpmverNew, rpmverFree, rpmverCmp, NULL, cstr, gc
from ._transaction import TransactionSet
from ._keyring import keyring
from ._const import *


def labelCompare(a, b):
    (e1, v1, r1) = a
    (e2, v2, r2) = b

    cs = partial(cstr, error=ValueError("invalid version"))

    rpmver1 = gc(rpmverNew(cs(e1, True), cs(v1), cs(r1, True)), rpmverFree)
    rpmver2 = gc(rpmverNew(cs(e2, True), cs(v2), cs(r2, True)), rpmverFree)

    return rpmverCmp(rpmver1, rpmver2)
