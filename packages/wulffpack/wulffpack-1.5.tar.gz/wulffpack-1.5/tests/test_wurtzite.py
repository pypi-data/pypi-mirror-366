import numpy as np
import pytest
from ase.build import bulk
from wulffpack import SingleCrystal


def test_wurtzite_fails():
    surface_energies = {
        (0, 0, 0, 1): 1,
        (1, 0, -1, 0): 2,
        (1, 1, -2, 0): 3,
    }
    prim = bulk('ZnSe', crystalstructure='wurtzite', a=4.0, c=6.6, u=0.37)
    with pytest.raises(ValueError) as excinfo:
        SingleCrystal(surface_energies, primitive_structure=prim, tol=1e-5)
        msg = str(excinfo)
        assert 'orthogonal' in msg
        assert 'closed shape' in msg
        assert 'Please review your input.' in msg


@pytest.fixture
def cases(request):
    if request.param == 0:
        return dict(
            surface_energies={
                (0, 0, 0, 1): 1,
                (0, 0, 0, -1): 1,
                (1, 0, -1, 0): 2,
                (1, 1, -2, 0): 3
            },
            volume=22863.0707,
            area=4875.43351040801,
            surface_energy=7313.150265612016,
            average_surface_energy=1.5,
            edge_length=372.4620,
            number_of_corners=12,
            facet_fractions={
                (0, 0, 0, 1): 0.25,
                (0, 0, 0, -1): 0.25,
                (1, 0, -1, 0): 0.5,
            }
        )
    elif request.param == 1:
        return dict(
            surface_energies={
                (0, 0, 0, 1): 0.5,
                (0, 0, 0, -1): 1.5,
                (1, 0, -1, 0): 1.7,
                (1, 1, -2, 0): 1.8
            },
            volume=22863.0707,
            area=4672.2904,
            surface_energy=6501.33,
            average_surface_energy=1.3914651427065274,
            edge_length=490.6579,
            number_of_corners=24,
            facet_fractions={
                (0, 0, 0, 1): 0.2319108571177545,
                (0, 0, 0, -1): 0.2319108571177545,
                (1, 0, -1, 0): 0.374775,
                (1, 1, -2, 0): 0.161403,
            }
        )


@pytest.mark.parametrize('cases', [(0), (1)], indirect=['cases'])
def test_wurtzite_passes(cases):
    prim = bulk('ZnSe', crystalstructure='wurtzite', a=4.0, c=6.6, u=0.37)
    particle = SingleCrystal(cases['surface_energies'], primitive_structure=prim, tol=1e-5)
    for k, v in cases.items():
        if k in ['surface_energies', 'facet_fractions']:
            continue
        assert np.isclose(getattr(particle, k), v)
    for facet, fraction in particle.facet_fractions.items():
        assert np.isclose(fraction, cases['facet_fractions'][facet])


@pytest.mark.parametrize('cases', [(0), (1)], indirect=['cases'])
def test_wurtzite_str(cases):
    prim = bulk('ZnSe', crystalstructure='wurtzite', a=4.0, c=6.6, u=0.37)
    particle = SingleCrystal(cases['surface_energies'], primitive_structure=prim, tol=1e-5)
    str_out = str(particle)
    html_out = str(particle._repr_html_())
    for k in cases:
        if k in ['surface_energies']:
            continue
        assert k in str(str_out)
        assert k in str(html_out)
