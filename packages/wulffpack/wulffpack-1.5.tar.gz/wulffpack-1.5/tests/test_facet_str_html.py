from ase.build import bulk
from wulffpack import SingleCrystal


def test_facet_str():
    prim = bulk('ZnSe', crystalstructure='wurtzite', a=4.0, c=6.6, u=0.37)
    surface_energies = {
        (0, 0, 0, 1): 0.5,
        (0, 0, 0, -1): 1.5,
        (1, 0, -1, 0): 1.7,
        (1, 1, -2, 0): 1.8
    }
    particle = SingleCrystal(surface_energies, primitive_structure=prim, tol=1e-5)
    facets = particle.facets
    assert len(facets) == 14

    facet = facets[0]
    expected = """----------------- Facet ------------------
normal           : [0. 0. 1.]
original_normal  : [0. 0. 1.]
energy           :       0.5000
original_grain   : True
symmetries       :
     0 : [1 0 0]
         [0 1 0]
         [0 0 1]
     1 : [ 1 -1  0]
         [1 0 0]
         [0 0 1]
     2 : [ 0 -1  0]
         [ 1 -1  0]
         [0 0 1]"""
    assert str(facet).startswith(expected)

    facet = facets[7]
    expected = """----------------- Facet ------------------
normal           : [ 0.8660254 -0.5        0.       ]
original_normal  : [ 0.8660254 -0.5        0.       ]
energy           :       1.7000
original_grain   : True
symmetries       :
     0 : [0 1 0]
         [-1  1  0]
         [0 0 1]
     1 : [ 1 -1  0]
         [ 0 -1  0]
         [0 0 1]"""
    assert str(facet) == expected


def test_facet_repr_html():
    prim = bulk('AlO', crystalstructure='zincblende', a=4.1)
    surface_energies = {
        (0, 0, 1): 0.65,
        (0, 1, 1): 1.5,
    }
    particle = SingleCrystal(surface_energies, primitive_structure=prim, tol=1e-5)
    facets = particle.facets
    assert len(facets) == 6
    facet = facets[0]
    expected = """<table border="1" class="dataframe"<thead><tr><th style="text-align: left;">Property</th><th>Value</th></tr></thead><tbody><tr><td style="text-align: left">normal                </td><td>[0. 0. 1.]</td><tr><tr><td style="text-align: left">original_normal       </td><td>[0. 0. 1.]</td><tr><tr><td style="text-align: left">energy                </td><td>      0.6500</td><tr><tr><td style="text-align: left">original_grain        </td><td>True</td><tr><tr><td style="text-align: left">symmetries</td><tr><tr><td>0</td><td>[1 0 0]<br>[0 1 0]<br>[0 0 1]</td></tr><tr><td>1</td><td>[-1  0  0]<br>[ 0 -1  0]<br>[0 0 1]</td></tr><tr><td>2</td><td>[0 1 0]<br>[1 0 0]<br>[0 0 1]</td></tr><tr><td>3</td><td>[ 0 -1  0]<br>[-1  0  0]<br>[0 0 1]</td></tr></tbody></table>"""  # noqa
    assert facet._repr_html_() == expected
