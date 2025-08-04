# Imported from rpmdyn.pth whenever python is starting up and
# rpmdyn is installed.
def install_rpm_module():
    import os

    # If explicitly disabled, do nothing.
    if os.environ.get("RPMDYN_HOOK", "1") != "1":
        return

    # If real rpm is importable, do nothing.
    try:
        import rpm
        return
    except:
        # FIXME: catch only the appropriate import error
        # RPM cannot be imported, we will continue with our hook.
        pass

    # OK, we really want to install ourselves.
    import sys
    from rpmdyn import _rpm
    sys.modules['rpm'] = _rpm


install_rpm_module()
