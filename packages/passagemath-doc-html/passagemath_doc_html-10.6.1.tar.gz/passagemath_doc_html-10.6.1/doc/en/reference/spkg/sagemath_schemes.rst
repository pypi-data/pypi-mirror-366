.. _spkg_sagemath_schemes:

=======================================================================================================================================================
sagemath_schemes: Schemes, varieties, elliptic curves, algebraic Riemann surfaces, modular forms, arithmetic dynamics
=======================================================================================================================================================

`passagemath <https://github.com/passagemath/passagemath>`__ is open
source mathematical software in Python, released under the GNU General
Public Licence GPLv2+.

It is a fork of `SageMath <https://www.sagemath.org/>`__, which has been
developed 2005-2025 under the motto “Creating a Viable Open Source
Alternative to Magma, Maple, Mathematica, and MATLAB”.

The passagemath fork uses the motto "Creating a Free Passage Between the
Scientific Python Ecosystem and Mathematical Software Communities."
It was created in October 2024 with the following goals:

-  providing modularized installation with pip,
-  establishing first-class membership in the scientific Python
   ecosystem,
-  giving `clear attribution of upstream
   projects <https://groups.google.com/g/sage-devel/c/6HO1HEtL1Fs/m/G002rPGpAAAJ>`__,
-  providing independently usable Python interfaces to upstream
   libraries,
-  offering `platform portability and integration testing
   services <https://github.com/passagemath/passagemath/issues/704>`__
   to upstream projects,
-  inviting collaborations with upstream projects,
-  `building a professional, respectful, inclusive
   community <https://groups.google.com/g/sage-devel/c/xBzaINHWwUQ>`__,
-  `[empowering Sage users to participate in the scientific Python ecosystem
   <https://github.com/passagemath/passagemath/issues/248](https://github.com/passagemath/passagemath/issues/248)https://github.com/passagemath/passagemath/issues/248>`__ by publishing packages,
-  developing a port to `Pyodide <https://pyodide.org/en/stable/>`__ for
   serverless deployment with Javascript,
-  developing a native Windows port.

`Full documentation <https://doc.sagemath.org/html/en/index.html>`__ is
available online.

passagemath attempts to support and provides binary wheels suitable for
all major Linux distributions and recent versions of macOS.

For the Linux aarch64 (ARM) platform, some third-party packages are still missing wheels;
see ` <https://github.com/passagemath/passagemath?tab=readme-ov-file#full-installation-of-passagemath-from-binary-wheels-on-pypi>`__
for instructions for building them from source.

Binary wheels for native Windows (x86_64) are are available for a subset of
the passagemath distributions. Use of the full functionality of passagemath
on Windows currently requires the use of Windows Subsystem for Linux (WSL)
or virtualization.

The supported Python versions in the passagemath 10.6.x series are 3.9.x-3.13.x.


About this pip-installable distribution package
-----------------------------------------------------------

This pip-installable source distribution `sagemath-schemes` is an experimental distribution of a part of the Sage Library.  Use at your own risk.  It provides a small subset of the modules of the Sage library ("sagelib", `sagemath-standard`).


What is included
----------------

* `Ideals and Varieties <https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/multi_polynomial_ideal.html>`_

* `Schemes <https://doc.sagemath.org/html/en/reference/schemes/index.html>`_

* `Plane and Space Curves <https://doc.sagemath.org/html/en/reference/curves/index.html>`_

* `Elliptic and Hyperelliptic Curves <https://doc.sagemath.org/html/en/reference/arithmetic_curves/index.html>`_

* `Modular Forms <https://doc.sagemath.org/html/en/reference/modfrm/index.html>`_

* `Modular Symbols <https://doc.sagemath.org/html/en/reference/modsym/index.html>`_

* `Modular Abelian Varieties <https://doc.sagemath.org/html/en/reference/modabvar/index.html>`_

* `Arithmetic Dynamical Systems <https://doc.sagemath.org/html/en/reference/dynamics/index.html#arithmetic-dynamical-systems>`_


Status
------

The wheel builds. Some Cython modules that depend on FLINT or NTL are excluded.

`sage.all__sagemath_schemes` can be imported.

Many tests fail; see ``known-test-failures.json``.

Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_elliptic_curves`
- :ref:`spkg_gmpy2`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_ppl`
- :ref:`spkg_python_build`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_flint`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_sagemath_polyhedra`
- :ref:`spkg_sagemath_singular`
- :ref:`spkg_scipy`

Version Information
-------------------

package-version.txt::

    10.6.1

version_requirements.txt::

    passagemath-schemes ~= 10.6.1.0


Equivalent System Packages
--------------------------

(none known)

