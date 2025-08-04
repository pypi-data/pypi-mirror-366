from ._ffi import gc, rpmKeyringNew, rpmKeyringFree


class keyring(object):
    def __init__(self):
        self.__kr = gc(rpmKeyringNew(), rpmKeyringFree)
