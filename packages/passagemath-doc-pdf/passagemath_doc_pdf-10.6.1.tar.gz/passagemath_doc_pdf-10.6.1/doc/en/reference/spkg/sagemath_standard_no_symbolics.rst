.. _spkg_sagemath_standard_no_symbolics:

================================================================================================
sagemath_standard_no_symbolics: Sage library without the symbolics subsystem
================================================================================================

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
-----------------------------------------------

This pip-installable source distribution `sagemath-standard-no-symbolics` is a distribution of a part of the Sage Library.

Its main purpose is as a technical tool for the modularization project, to test that large parts of the Sage library are independent of the symbolics subsystem.

Type
----

standard


Dependencies
------------

- $(BLAS)
- $(MP_LIBRARY)
- $(PCFILES)
- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- $(SCRIPTS)
- :ref:`spkg_boost_cropped`
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_eclib`
- :ref:`spkg_ecm`
- :ref:`spkg_flint`
- :ref:`spkg_fpylll`
- :ref:`spkg_gap`
- :ref:`spkg_givaro`
- :ref:`spkg_glpk`
- :ref:`spkg_gmpy2`
- :ref:`spkg_gsl`
- :ref:`spkg_iml`
- :ref:`spkg_importlib_metadata`
- :ref:`spkg_importlib_resources`
- :ref:`spkg_jupyter_core`
- :ref:`spkg_lcalc`
- :ref:`spkg_libbraiding`
- :ref:`spkg_libgd`
- :ref:`spkg_libhomfly`
- :ref:`spkg_libpng`
- :ref:`spkg_linbox`
- :ref:`spkg_lrcalc_python`
- :ref:`spkg_m4ri`
- :ref:`spkg_m4rie`
- :ref:`spkg_memory_allocator`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfi`
- :ref:`spkg_mpfr`
- :ref:`spkg_ntl`
- :ref:`spkg_numpy`
- :ref:`spkg_pari`
- :ref:`spkg_pip`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_ppl`
- :ref:`spkg_pplpy`
- :ref:`spkg_primecount`
- :ref:`spkg_primecountpy`
- :ref:`spkg_primesieve`
- :ref:`spkg_pythran`
- :ref:`spkg_requests`
- :ref:`spkg_rw`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_brial`
- :ref:`spkg_sagemath_cddlib`
- :ref:`spkg_sagemath_combinat`
- :ref:`spkg_sagemath_eclib`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_giac`
- :ref:`spkg_sagemath_graphs`
- :ref:`spkg_sagemath_groups`
- :ref:`spkg_sagemath_homfly`
- :ref:`spkg_sagemath_lcalc`
- :ref:`spkg_sagemath_libbraiding`
- :ref:`spkg_sagemath_libecm`
- :ref:`spkg_sagemath_linbox`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_sagemath_ntl`
- :ref:`spkg_sagemath_pari`
- :ref:`spkg_sagemath_plot`
- :ref:`spkg_sagemath_polyhedra`
- :ref:`spkg_sagemath_repl`
- :ref:`spkg_sagemath_schemes`
- :ref:`spkg_sagemath_singular`
- :ref:`spkg_sagemath_tachyon`
- :ref:`spkg_singular`
- :ref:`spkg_symmetrica`
- :ref:`spkg_typing_extensions`

Version Information
-------------------

package-version.txt::

    10.6.1

version_requirements.txt::

    passagemath-standard-no-symbolics ~= 10.6.1.0


Equivalent System Packages
--------------------------

(none known)

