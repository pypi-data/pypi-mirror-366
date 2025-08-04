from cffi import FFI

ffi = FFI()
ffi.cdef(
    """
    typedef void* Header;
    typedef void* FD_t;
    typedef void* rpm_data_t;
    typedef void* rpmKeyring;
    typedef uint32_t rpm_count_t;
    typedef int32_t rpmTagVal;
    typedef int32_t rpmTagType;
    typedef int32_t rpmTagClass;
    typedef int32_t rpmTagReturnType;
    typedef uint32_t rpmtdFlags;

    /*
        We'd rather not depend on RPM's data structures, but in this case we
        do copy this declaration since:

        - it's not opaque in RPM - it is really in the public headers. So presumably
          it won't be changed often (hopefully ever) as that would not be
          ABI-compatible.

        - best I can tell, there is no public API which makes it possible to get
          at raw data of type RPM_BIN_TYPE. The native python bindings rely on
          internals to make those headers readable. We do the same since there is
          no other choice as far as I can see.
    */
    struct rpmtd_s {
        int32_t tag;	/* rpm tag of this data entry*/
        int32_t type;	/* data type */
        rpm_count_t count;	/* number of entries */
        rpm_data_t data;	/* pointer to actual data */
        rpmtdFlags flags;	/* flags on memory allocation etc */
        int ix;		/* iteration index */
        rpm_count_t size;	/* size of data (only works for RPMTD_IMMUTABLE atm) */
    };
    typedef struct rpmtd_s* rpmtd;

    void* rpmverNew(const char *e, const char *v, const char *r);
    void* rpmverFree(void*);
    int rpmverCmp(void*, void*);

    rpmTagReturnType rpmTagGetReturnType(rpmTagVal);

    FD_t fdDup(int);
    int Fclose(FD_t);

    rpmtd rpmtdNew();
    rpmtd rpmtdFree(void*);
    rpm_count_t rpmtdCount(rpmtd);
    rpmTagVal rpmtdTag(rpmtd);
    rpmTagType rpmtdType(rpmtd);
    rpmTagClass rpmtdClass(rpmtd);
    rpmtdFlags rpmtdGetFlags(rpmtd);
    const char* rpmtdGetString(rpmtd);
    uint64_t rpmtdGetNumber(rpmtd);
    const char* rpmtdNextString(rpmtd);
    int rpmtdFromUint8(rpmtd, rpmTagVal, uint8_t*, rpm_count_t);

    int rpmtdInit(rpmtd);
    int rpmtdNext(rpmtd);

    rpmKeyring rpmKeyringNew();
    rpmKeyring rpmKeyringFree(rpmKeyring);

    void* rpmtsCreate();
    void* rpmtsFree(void*);
    int rpmtsSetKeyring(void*, rpmKeyring);
    uint32_t rpmtsSetVSFlags(void*, uint32_t);
    uint32_t rpmtsVSFlags(void*);

    int rpmReadPackageFile(void*, void*, const char*, Header*);

    Header headerNew();
    Header headerFree(void*);
    int headerGet(Header, int32_t, void*, uint32_t);

    int rpmExpandNumeric(const char*);
"""
)

rpm = ffi.dlopen("rpm")
rpmio = ffi.dlopen("rpmio")

NULL = ffi.NULL
gc = ffi.gc


def cstr(value, nullable=False, error=None):
    if value is None and nullable:
        return NULL
    if value is None and not nullable:
        error = error or TypeError("expected str, got None")
        raise error
    return value.encode("utf-8")


rpmverNew = rpmio.rpmverNew
rpmverFree = rpmio.rpmverFree
rpmverCmp = rpmio.rpmverCmp

rpmTagGetReturnType = rpm.rpmTagGetReturnType
fdDup = rpmio.fdDup
Fclose = rpmio.Fclose

rpmtdNew = rpm.rpmtdNew
rpmtdFree = rpm.rpmtdFree
rpmtdCount = rpm.rpmtdCount
rpmtdTag = rpm.rpmtdTag
rpmtdType = rpm.rpmtdType
rpmtdClass = rpm.rpmtdClass
rpmtdGetFlags = rpm.rpmtdGetFlags
rpmtdGetString = rpm.rpmtdGetString
rpmtdGetNumber = rpm.rpmtdGetNumber
rpmtdNextString = rpm.rpmtdNextString
rpmtdInit = rpm.rpmtdInit
rpmtdNext = rpm.rpmtdNext
rpmtdFromUint8 = rpm.rpmtdFromUint8

rpmtsCreate = rpm.rpmtsCreate
rpmtsFree = rpm.rpmtsFree
rpmtsSetVSFlags = rpm.rpmtsSetVSFlags
rpmtsVSFlags = rpm.rpmtsVSFlags
rpmtsSetKeyring = rpm.rpmtsSetKeyring

rpmReadPackageFile = rpm.rpmReadPackageFile

headerNew = rpm.headerNew
headerFree = rpm.headerFree
headerGet = rpm.headerGet

rpmKeyringNew = rpm.rpmKeyringNew
rpmKeyringFree = rpm.rpmKeyringFree

rpmExpandNumeric = rpm.rpmExpandNumeric
