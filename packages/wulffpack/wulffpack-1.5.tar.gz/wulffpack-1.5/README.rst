WulffPack
=========

**WulffPack** is a tool for making Wulff constructions, typically for
minimizing the energy of nanoparticles. A detailed description of the
functionality provided as well as an extensive tutorial can be found in the
`user guide <https://wulffpack.materialsmodeling.org>`_.

**WulffPack** constructs both continuum models and atomistic structures for
further modeling with, e.g., molecular dynamics or density functional theory.

.. code-block:: python

    from wulffpack import SingleCrystal
    from ase.io import write
    surface_energies = {(1, 1, 1): 1.0, (1, 0, 0): 1.2}
    particle = SingleCrystal(surface_energies)
    particle.view()
    write('atoms.xyz', particle.atoms)

With the help of `ASE <https://wiki.fysik.dtu.dk/ase>`_ and 
`Spglib <https://spglib.readthedocs.io/>`_, **WulffPack** handles any
crystalline symmetry. **WulffPack** also provides the backbone of 
`a web application in SHARC
<https://sharc.materialsmodeling.org/wulff_construction>`_,
in which Wulff constructions for cubic crystals can be created interactively.

Installation
------------

In the most simple case, **WulffPack** can be installed using pip as follows::

    pip3 install wulffpack --user

or alternatively::

    python3 -m pip install wulffpack --user


**WulffPack** is based on Python3 and invokes functionality from other Python
libraries including

* `ASE <https://wiki.fysik.dtu.dk/ase>`_,
* `Spglib <https://spglib.readthedocs.io/>`_,
* `NumPy <https://www.numpy.org/>`_,
* `SciPy <https://docs.scipy.org>`_, and
* `Matplotlib <https://matplotlib.org/>`_.

Credits
-------

**WulffPack** has been developed at Chalmers University of Technology in
Gothenburg (Sweden) in the `Condensed Matter and Materials Theory division
<https://www.materialsmodeling.org>`_ at the Department of Physics.

When using **WulffPack** in your research please cite

| J. Magnus Rahm and Paul Erhart
| *WulffPack: A Python package for Wulff constructions*
| J. Open Source Softw. **5**, 1944 (2020)
| `doi: 10.21105/joss.01944 <https://doi.org/10.21105/joss.01944>`_

Contribute
----------

Bugs and feature requests should be submitted via the
`gitlab issue tracker <https://gitlab.com/materials-modeling/wulffpack/issues>`_.
