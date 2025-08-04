from io import IOBase

from ._ffi import gc, cstr
from . import _ffi, _const


HEADERGET_EXT = 2

RPM_NULL_TYPE = 0
RPM_CHAR_TYPE = 1
RPM_INT8_TYPE = 2
RPM_INT16_TYPE = 3
RPM_INT32_TYPE = 4
RPM_INT64_TYPE = 5
RPM_STRING_TYPE = 6
RPM_BIN_TYPE = 7
RPM_STRING_ARRAY_TYPE = 8
RPM_I18NSTRING_TYPE = 9


RPM_ANY_RETURN_TYPE = 0
RPM_SCALAR_RETURN_TYPE = 0x00010000
RPM_ARRAY_RETURN_TYPE = 0x00020000
RPM_MAPPING_RETURN_TYPE = 0x00040000
RPM_MASK_RETURN_TYPE = 0xFFFF0000


class Header(object):
    def __init__(self, h):
        self.__h = h

    def __getitem__(self, key):
        td = gc(_ffi.rpmtdNew(), _ffi.rpmtdFree)

        # Result intentionally not checked - official bindings do the same.
        _ffi.headerGet(self.__h, key, td, HEADERGET_EXT)

        # TODO: check flags: _ffi.rpmtdGetFlags(td)

        rtype = _ffi.rpmTagGetReturnType(key)
        is_array = (rtype & RPM_MASK_RETURN_TYPE) == RPM_ARRAY_RETURN_TYPE

        td_type = _ffi.rpmtdType(td)

        def unimplemented(_td):
            raise NotImplementedError(key)

        get_value = unimplemented

        def get_string(x):
            # TODO: this will return unicode strings.
            # It is compatible with modern versions of rpm, but not older.
            # Should we try to support both?
            # TODO: and is it right to assume utf8?
            return _ffi.ffi.string(_ffi.rpmtdGetString(x)).decode("utf-8")

        out = []

        if td_type == RPM_NULL_TYPE:
            get_value = lambda _: None
        elif td_type == RPM_CHAR_TYPE:
            # FIXME: find an RPM using this type
            pass
        elif td_type in [RPM_INT8_TYPE, RPM_INT16_TYPE, RPM_INT32_TYPE, RPM_INT64_TYPE]:
            get_value = _ffi.rpmtdGetNumber
        elif td_type == RPM_STRING_TYPE:
            get_value = get_string
        elif td_type == RPM_BIN_TYPE:
            # bytes_offset = td_data_offset()
            bytes_count = td.count

            data = _ffi.ffi.cast("char*", td.data)
            bytes = _ffi.ffi.unpack(data, bytes_count)
            get_value = lambda x: bytes
        elif td_type == RPM_STRING_ARRAY_TYPE:
            # TODO: what's the deal with this vs RPM_ARRAY_RETURN_TYPE & string?
            get_value = get_string
        elif td_type == RPM_I18NSTRING_TYPE:
            # FIXME: find an RPM using this type
            pass

        _ffi.rpmtdInit(td)

        for _ in range(0, 100000):
            if _ffi.rpmtdNext(td) == -1:
                break
            out.append(get_value(td))

        if is_array:
            return out

        if out:
            return out[0]

        return None


class TransactionSet(object):
    def __init__(self):
        self.__ts = gc(_ffi.rpmtsCreate(), _ffi.rpmtsFree)

        # native bindings set a default vsflags
        flags = _ffi.rpmExpandNumeric(cstr("%{?__vsflags}"))
        self.setVSFlags(flags)

    def setKeyring(self, keyring):
        return _ffi.rpmtsSetKeyring(self.__ts, keyring._keyring__kr if keyring else _ffi.NULL)

    def setVSFlags(self, flags):
        return _ffi.rpmtsSetVSFlags(self.__ts, flags)

    def getVSFlags(self):
        return _ffi.rpmtsVSFlags(self.__ts)

    def hdrFromFdno(self, fd):
        # Accept the Buffered I/O stream object as fd. It inherits IOBase
        # the proides the underlying FD number where available.
        if isinstance(fd, IOBase):
            fd = fd.fileno()

        assert isinstance(fd, int)

        rpmfd = gc(_ffi.fdDup(fd), _ffi.Fclose)

        h = _ffi.ffi.new("Header*")
        res = _ffi.rpmReadPackageFile(
            self.__ts,
            rpmfd,
            _ffi.NULL,
            h,
        )

        # TODO: raise proper exceptions
        assert res == _const.RPMRC_OK

        return Header(gc(_ffi.ffi.cast("Header", h[0]), _ffi.headerFree))
