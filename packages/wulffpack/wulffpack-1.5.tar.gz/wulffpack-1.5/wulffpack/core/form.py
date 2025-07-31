from typing import List, Dict, Union
import numpy as np
from .facet import Facet
from .geometry import (is_array_in_arrays,
                       where_is_array_in_arrays)


class Form():
    """
    A `Form` object contains all facets that are equivalent by the
    symmetry of the system under consideration. For a cubic system,
    this means that the form with Miller indices {100} will contain
    the facets with normals [100], [-100], [010] etc.

    Parameters
    ----------
    miller_indices
        Miller indices for a representative member of the form.
    energy
        The surface energy per area for a facet in this form.
    cell
        The cell, with the basis vectors as columns.
    symmetries
        Symmetry elements of the system. If symmetry is broken
        by, e.g., the presence of an interface, this list
        should only contain the symmetries surviving.
    parent_miller_indices
        If symmetry is broken, it may still be of interest to
        know what its form would be had not the symmetry been
        broken. This attribute contains the Miller indices for
        a representative of such a form.
    """

    def __init__(self, miller_indices: tuple,
                 energy: float,
                 cell: np.ndarray,
                 symmetries: List[np.ndarray],
                 parent_miller_indices: tuple):
        self.miller_indices = miller_indices
        self.energy = energy
        self.parent_miller_indices = parent_miller_indices

        # Create all facets belonging to this form
        self.facets = []
        used_normals = []
        reciprocal_cell = np.linalg.inv(cell).T
        normal = np.dot(reciprocal_cell, self.miller_indices)
        normal_scaled = np.linalg.solve(cell, normal)
        for R in symmetries:
            new_normal_scaled = np.dot(R, normal_scaled)
            new_normal = np.dot(cell, new_normal_scaled)
            array_index = where_is_array_in_arrays(new_normal, used_normals)
            if array_index == -1:
                # Then we found a new facet
                self.facets.append(Facet(normal=tuple(new_normal),
                                         energy=energy,
                                         symmetry=R))
                used_normals.append(new_normal)
            else:
                # If the facet was already there, save instead the
                # symmetry operation that took us there
                facet = self.facets[array_index]
                assert np.allclose(facet.normal, new_normal / np.linalg.norm(new_normal))
                facet.symmetries.append(R)

    def __str__(self) -> str:
        width = 38
        s = []
        s += ['{s:-^{n}}'.format(s=' Form ', n=width)]
        flds = dict(miller_indices='', parent_miller_indices='',
                    area='12.4f', surface_energy='12.2f', edge_length='12.4f')
        for fld, fmt in flds.items():
            s += ['{fld:22} : {value:{fmt}}'.format(fld=fld, value=getattr(self, fld), fmt=fmt)]
        return '\n'.join(s)

    def _repr_html_(self) -> str:
        s = []
        s += ['<table border="1" class="dataframe"']
        s += [
            '<thead><tr><th style="text-align: left;">Property</th><th>Value</th></tr></thead>'
        ]
        s += ['<tbody>']
        flds = dict(miller_indices='', parent_miller_indices='',
                    area='12.4f', surface_energy='12.2f', edge_length='12.4f')
        for fld, fmt in flds.items():
            s += [
                f'<tr><td style="text-align: left">{fld:22}</td>'
                '<td>{value:{fmt}}</td><tr>'.format(value=getattr(self, fld), fmt=fmt)
            ]
        s += ['</tbody>']
        s += ['</table>']
        return ''.join(s)

    @property
    def area(self) -> float:
        """Returns the total area of the facets in this form."""
        return len(self.facets) * self.facets[0].area

    @property
    def surface_energy(self) -> float:
        """Returns the total surface energy of the facets in this form."""
        return len(self.facets) * self.facets[0].surface_energy

    @property
    def volume(self) -> float:
        """
        Returns the total volume formed by pyramids formed by each
        facet and the origin.
        """
        return len(self.facets) * self.facets[0].get_volume()

    @property
    def edge_length(self) -> float:
        """Returns the length of all facets in the form."""
        return len(self.facets) * self.facets[0].perimeter_length


def setup_forms(surface_energies: Dict,
                cell: np.ndarray,
                symmetries_restricted: List[np.ndarray],
                symmetries_full: List[np.ndarray],
                twin_boundary: Union[List, tuple] = None,
                interface: Union[List, tuple] = None,
                tol: float = 1e-6) -> Dict:
    """
    Create an adapted dictionary of surface energies based on
    the symmetries specified.

    This function is relevant for polycrystalline particles, the crystal
    structure of which possess higher symmetry than the grains they are made
    from. A decahedron, for example, is made of five FCC grains. FCC, being a
    cubic crystal lattice, has 48 symmetry elements, but the grain is one of
    five and has much fewer symmetry elements. This means that there are
    multiple facets that would belong to the {111} form had not the symmetry
    been broken. In the decahedral case, there are thus three inequivalent
    families of facets that in the cubic case would all have been equivalent
    facets belonging to the {111} form. These three families are, respectively,
    the twin facets, the usually large facets "on top and underneath" the
    particle as well as the re-entrance facets(the "notches"). All of these
    will get their own key in the dictionary, describing a representative
    member of the form.

    Parameters
    ----------
    surface_energies
        keys are either tuples with three integers (describing a form in the
        cubic case) or the string `'twin'`/`'interface'`, values are
        corresponding surface energies
    cell
        the basis vectors as columns
    symmetries_restricted
        the matrices for the symmetry elements in the broken symmetry
    symmetry_full
        the matrices for the symmetry elements in the case of full symmetry
        (for example the 48 symmetry elements of the m-3m point group)
    twin_boundary
        Miller index for a twin boundary if there is one
    interface
        Miller index for an interface(to a substrate for example)
    tol
        Numerical tolerance when checking if energies are identical

    Returns
    -------
    dictionary
        keys are tuples describing the form(for each inequivalent form in the
        broken symmetry case) with three integer, values are corresponding
        surface energies
    """
    reciprocal_cell = np.linalg.inv(cell).T
    forms = []
    scaled_normals = []  # To be able to identify over-specified facets
    ordered_facets = []  # --"--
    if min(e for form, e in surface_energies.items() if form != 'interface') < 0:
        raise ValueError('Please use only positive surface/twin energies')

    for form, energy in surface_energies.items():
        inequivalent_normals_scaled = []
        if form == 'twin':
            if twin_boundary:
                forms.append(Form(miller_indices=twin_boundary,
                                  energy=energy / 2,
                                  cell=cell,
                                  symmetries=symmetries_restricted,
                                  parent_miller_indices=form))
        elif form == 'interface':
            if interface:
                forms.append(Form(miller_indices=interface,
                                  energy=energy,
                                  cell=cell,
                                  symmetries=symmetries_restricted,
                                  parent_miller_indices=form))
        else:
            if len(form) == 4:
                miller_indices = convert_bravais_miller_to_miller(form)
            else:
                miller_indices = form
            normal = np.dot(reciprocal_cell, miller_indices)  # Cartesian coords
            normal_scaled = np.linalg.solve(cell, normal)  # scaled coords

            # Check that this facet is not symmetrically equivalent to another
            scaled_normals.append(normal_scaled)
            ordered_facets.append((form, energy))
            for R_r in symmetries_full:
                transformed_normal_scaled = np.dot(R_r, normal_scaled)

                previous_index = where_is_array_in_arrays(transformed_normal_scaled,
                                                          scaled_normals[:-1])
                if previous_index != -1:
                    # Then this facet is redundant.
                    # If it has the same energy, we just skip it,
                    # otherwise we need to throw an exception.
                    if abs(energy - ordered_facets[previous_index][1]) > tol:
                        raise ValueError(
                            f'The Miller indices {form} '
                            f'are equivalent to {ordered_facets[previous_index][0]} '
                            'by symmetry. If your system is such that they should be '
                            'inequivalent, please specify a primitive structure with '
                            'the appropriate point group symmetry or provide a '
                            'custom set of symmetries.')
                    else:
                        break
            else:
                # Then this facet is not symmetrically equivalent to another.
                # Now we need to look at all symmetrically equivalent versions
                # and check whether broken symmetry makes them inequivalent.
                for R_r in symmetries_full:
                    transformed_normal_scaled = np.dot(R_r, normal_scaled)
                    for R_f in symmetries_restricted:
                        if is_array_in_arrays(np.dot(R_f, transformed_normal_scaled),
                                              inequivalent_normals_scaled):
                            break
                    else:
                        transformed_normal = np.dot(cell, transformed_normal_scaled)
                        miller = np.linalg.solve(reciprocal_cell, transformed_normal)
                        rounded_miller = np.round(miller)
                        assert np.allclose(miller, rounded_miller)
                        rounded_miller = tuple(int(i) for i in rounded_miller)
                        forms.append(Form(miller_indices=rounded_miller,
                                          energy=energy,
                                          cell=cell,
                                          symmetries=symmetries_restricted,
                                          parent_miller_indices=form))
                        inequivalent_normals_scaled.append(transformed_normal_scaled)
    return forms


def convert_bravais_miller_to_miller(bravais_miller_indices: tuple) -> tuple:
    """
    Returns the Miller indices(three integer tuple)
    corresponding to Bravais-Miller indices(for integer
    tuple).

    Paramters
    ---------
    bravais_miller_indices
        Four integer tuple
    """
    if sum(bravais_miller_indices[:3]) != 0:
        raise ValueError('Invalid Bravais-Miller indices (h, k, i, l), '
                         'h + k + i != 0')
    return tuple(bravais_miller_indices[i] for i in [0, 1, 3])
