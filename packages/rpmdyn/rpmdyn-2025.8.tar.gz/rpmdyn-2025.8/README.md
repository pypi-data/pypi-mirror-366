# rpmdyn

Alternative dynamic RPM bindings for Python.

[![PyPI](https://img.shields.io/pypi/v/rpmdyn)](https://pypi.org/project/rpmdyn/)

<!--TOC-->

- [rpmdyn](#rpmdyn)
  - [Overview](#overview)
  - [Usage](#usage)
  - [License](#license)

<!--TOC-->

## Overview

`rpmdyn` provides an alternative means of using the `rpm` library from Python
via dynamic binding (FFI).

This project is intended to support testing Python code based on the `rpm`
library in CI or development environments where installing official bindings is
too much of a hassle. You may find it useful if you have tried `rpm-py-installer`
and ran into problems with it.

**⚠️Major caveat⚠️**: the provided RPM bindings are *far from complete*!
Bindings have been implemented "on demand" to fit the author's needs.

Here's a comparison between a few different ways of accessing RPM Python
bindings to help you understand if this project may be of use to you:

|                                    | OS package | `rpmdyn` | `rpm-py-installer` |
| ---------------------------------- | ---------- | -------- | ------------------ |
| pip-installable from PyPI?         | ❌   | ✅  | ✅  |
| Usable in virtualenv?              | ❌¹  | ✅  | ✅  |
| Supports multiple Python versions? | ❌²  | ✅  | ✅  |
| No compilers/headers needed?       | ✅   | ✅  | ❌³ |
| Secure supply chain?               | ✅   | ✅  | ❌⁴ |
| Complete bindings?                 | ✅   | ❌⁵ | ✅  |

1. Only usable if you enable system site-packages, which is generally unacceptable.
2. While there are no hard and fast rules around what kinds of packages a Linux distribution
   provides, it is common for a distribution to choose one primary supported Python version
   and only provide libraries for that version.
3. `rpm-py-installer` works by compiling RPM bindings and thus needs a compiler.
4. `rpm-py-installer` downloads RPM sources insecurely with no validation of checksums
   or signatures. This is an issue if you only want to use known versions of all dependencies,
   and will not work at all in a firewalled setup (e.g. which only allows access to an internal
   PyPI registry).
5. `rpmdyn` implements only a small subset of RPM bindings, as bindings need to be implemented
   manually. The set of available bindings reflects the needs of `rpmdyn` contributors.

## Usage

Install `rpmdyn` and it will automatically be used by default:

- if real (native) RPM bindings are available, then `import rpm` will use those.
- otherwise, `import rpm` will use `rpmdyn`.

This is achieved via a PTH hook. If you wish to disable this behavior,
set the `RPMDYN_HOOK` environment variable to `0`.

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
