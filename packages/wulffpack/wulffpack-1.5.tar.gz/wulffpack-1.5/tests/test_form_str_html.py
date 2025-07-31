from ase.build import bulk
from wulffpack import SingleCrystal


def test_form_str():
    prim = bulk('ZnSe', crystalstructure='wurtzite', a=4.0, c=6.6, u=0.37)
    surface_energies = {
        (0, 0, 0, 1): 0.5,
        (0, 0, 0, -1): 1.5,
        (1, 0, -1, 0): 1.7,
        (1, 1, -2, 0): 1.8
    }
    particle = SingleCrystal(surface_energies, primitive_structure=prim, tol=1e-5)
    forms = particle.forms
    assert len(forms) == 4
    form = forms[0]
    expected = """---------------- Form ----------------
miller_indices         : (0, 0, 1)
parent_miller_indices  : (0, 0, 0, 1)
area                   :    1083.5549
surface_energy         :       541.78
edge_length            :     118.7286"""
    assert str(form) == expected


def test_form_repr_html():
    prim = bulk('AlO', crystalstructure='zincblende', a=4.1)
    surface_energies = {
        (0, 0, 1): 0.65,
        (0, 1, 1): 1.5,
    }
    particle = SingleCrystal(surface_energies, primitive_structure=prim, tol=1e-5)
    forms = particle.forms
    assert len(forms) == 1
    form = forms[0]
    expected = """<table border="1" class="dataframe"<thead><tr><th style="text-align: left;">Property</th><th>Value</th></tr></thead><tbody><tr><td style="text-align: left">miller_indices        </td><td>(0, 0, 1)</td><tr><tr><td style="text-align: left">parent_miller_indices </td><td>(0, 0, 1)</td><tr><tr><td style="text-align: left">area                  </td><td>   2521.5000</td><tr><tr><td style="text-align: left">surface_energy        </td><td>     1638.97</td><tr><tr><td style="text-align: left">edge_length           </td><td>    492.0000</td><tr></tbody></table>"""  # noqa
    assert form._repr_html_() == expected
