from typing import Dict, Tuple, List
import numpy as np
from ase import Atoms
from .core import BaseParticle
from .core.form import setup_forms
from .core.geometry import (get_standardized_structure,
                            get_symmetries,
                            get_angle,
                            get_rotation_matrix,
                            break_symmetry,
                            is_array_in_arrays)


class Icosahedron(BaseParticle):
    """
    An `Icosahedron` object is a generalized Wulff construction
    of an icosahedral particle.

    Parameters
    ----------
    surface_energies
        A dictionary with surface energies, where keys are
        Miller indices and values surface energies (per area)
        in a unit of choice, such as J/m^2.
    twin_energy
        Energy per area for twin boundaries
    primitive_structure
        Primitive cell to define the atomic structure used if an atomic
        structure is requested. By default, an Au FCC structure is used.
        The crystal has to have cubic symmetry.
    natoms
        Together with `lattice_parameter`, this parameter
        defines the volume of the particle. If an atomic structure
        is requested, the number of atoms will as closely as possible
        match this value.
    symprec
        Numerical tolerance for symmetry analysis, forwarded to spglib.
    tol
        Numerical tolerance parameter.

    Example
    -------
    The following example illustrates some possible uses of an
    `Icosahedron` object::

        >>> from wulffpack import Icosahedron
        >>> from ase.build import bulk
        >>> from ase.io import write
        >>> surface_energies = {(1, 1, 1): 1.0, (1, 0, 0): 1.14}
        >>> particle = Icosahedron(surface_energies,
        ...                        twin_energy=0.03,
        ...                        primitive_structure=bulk('Au'))
        >>> particle.view()
        >>> write('icosahedron.xyz', particle.atoms) # Writes atomic structure

    """

    def __init__(self,
                 surface_energies: Dict[tuple, float],
                 twin_energy: float,
                 primitive_structure: Atoms = None,
                 natoms: int = 1000,
                 symprec: float = 1e-5,
                 tol: float = 1e-5):
        standardized_structure = get_standardized_structure(primitive_structure, symprec=symprec)
        symmetries = get_symmetries(standardized_structure, symprec=symprec)
        if len(symmetries) < 48:
            raise ValueError('An icosahedron can only be created with a '
                             'primitive structure that has cubic symmetry')

        broken_symmetries = break_symmetry(symmetries, [(1, 1, 1)])

        if twin_energy > 0.5 * min(surface_energies.values()):
            raise ValueError('The construction expects a twin energy '
                             'that is smaller than 50 percent of the '
                             'smallest surface energy.')
        surface_energies = surface_energies.copy()
        surface_energies['twin'] = twin_energy

        forms = setup_forms(surface_energies,
                            standardized_structure.cell.T,
                            broken_symmetries,
                            symmetries,
                            twin_boundary=(-1, -1, 1))

        super().__init__(forms=forms,
                         standardized_structure=standardized_structure,
                         natoms=natoms,
                         ngrains=20,
                         volume_scale=_get_icosahedral_scale_factor()**2,
                         tol=tol)

        # Duplicate the single tetrahedron to form a complete icosahedron
        # with 20 tetrahedra

        # Translate such that tip of the tetrahedron is in the origin
        min_proj = 1e12
        for vertex in self._twin_form.facets[0].vertices:
            proj = np.dot(vertex, (1, 1, 1))
            if proj < min_proj:
                min_proj = proj
                translation = - vertex
        self.translate_particle(translation)

        # Back up the vertices in a separate list
        # (that list is useful if creating an Atoms object)
        for facet in self._yield_facets():
            facet.original_vertices = [vertex.copy() for vertex in facet.vertices]

        # Increase the distance from 111 to fill space
        middle = np.array([1., 1., 1.])
        middle /= np.linalg.norm(middle)
        for facet in self._yield_facets():
            for i, vertex in enumerate(facet.vertices):
                if np.allclose(vertex, [0, 0, 0]):
                    continue
                dist = vertex - np.dot(vertex, middle) * middle
                facet.vertices[i] = vertex + (_get_icosahedral_scale_factor() - 1) * dist
            # Tilt the normal
            previous_normal = facet.normal
            facet.normal = np.cross(facet.vertices[1] - facet.vertices[0],
                                    facet.vertices[2] - facet.vertices[0])
            if get_angle(facet.normal, previous_normal) > np.pi / 2:
                facet.normal *= -1
            facet.normal /= np.linalg.norm(facet.normal)

        # Make 20 grains
        symmetries = self._get_symmetry_operations()
        self._duplicate_particle(symmetries)

    @property
    def atoms(self) -> Atoms:
        """
        Returns an ASE Atoms object
        """
        atoms = self._get_atoms()

        # Handle fivefold axes and twin faces separately
        # (they will be duplicated otherwise)
        max_projections_twin = [-1e9, -1e9, -1e9]
        twin_normals = [self._twin_form.facets[i].original_normal for i in range(3)]

        # Find max projections onto twin directions
        for atom in atoms:
            for i, normal in enumerate(twin_normals):
                projection = np.dot(normal, atom.position)
                if projection > max_projections_twin[i]:
                    max_projections_twin[i] = projection

        # Now identify all atoms that are
        # close to the maximum projection
        fivefold_atoms = Atoms()
        twin_indices = [set(), set(), set()]
        for atom in atoms:
            for i, normal in enumerate(twin_normals):
                projection = np.dot(normal, atom.position)
                if abs(projection - max_projections_twin[i]) < 1e-5:
                    twin_indices[i].add(atom.index)

        # Since they should not be duplicated we will remove them from
        # the atoms object eventually
        to_remove = list(twin_indices[0].union(*twin_indices[1:]))

        # Identify the central atom
        central_atom = list(twin_indices[0].intersection(*twin_indices[1:]))
        if central_atom:
            assert len(central_atom) == 1
            for twin in twin_indices:
                twin.remove(central_atom[0])
            central_atom = atoms[central_atom[0]]

        # Identify the fivefold axes
        fivefold_axes = []
        fivefold_atoms = []
        for i in range(3):
            fivefold_axes.append(twin_indices[i].intersection(twin_indices[(i + 1) % 3]))
        for fivefold_axis in fivefold_axes:
            fivefold_atoms.append(atoms[list(fivefold_axis)])
            for ind in fivefold_axis:
                for i in range(3):
                    twin_indices[i].discard(ind)
        twin_atoms = []
        for twin in twin_indices:
            twin_atoms.append(atoms[list(twin)])
        del atoms[to_remove]
        tetrahedron_atoms = atoms.copy()

        # Increase the distance from 111 for each vertex to fill space
        middle = np.array([1., 1., 1.])
        middle /= np.linalg.norm(middle)
        for atoms in [tetrahedron_atoms, *twin_atoms, *fivefold_atoms]:
            for atom in atoms:
                if np.allclose(atom.position, [0, 0, 0]):
                    continue
                dist = atom.position - np.dot(atom.position, middle) * middle
                atom.position = atom.position + (_get_icosahedral_scale_factor() - 1) * dist

        # Make 20 grains
        symmetries = self._get_all_symmetry_operations()
        new_positions = []

        # Add the "bulk" of each tetrahedron
        base_tetrahedron = np.array([1., 1., 1])
        new_positions += _get_unique_coordinates(tetrahedron_atoms, symmetries, base_tetrahedron)

        # Add the atoms on the 30 twin boundaries
        base_twin = np.array(sum(atom.position for atom in twin_atoms[0]))
        new_positions += _get_unique_coordinates(twin_atoms[0], symmetries, base_twin)

        # Add the atoms along the fivefold axes
        base_fivefold = np.array(sum(atom.position for atom in fivefold_atoms[0]))
        new_positions += _get_unique_coordinates(fivefold_atoms[0], symmetries, base_fivefold)

        atoms = Atoms('{}{}'.format(self.standardized_structure[0].symbol,
                                    len(new_positions)),
                      positions=new_positions)
        atoms.append(central_atom)
        return atoms

    def _get_two_fivefold_axes(self) -> Tuple[np.ndarray]:
        """
        Identify two fivefold axes as the two vertices which
        are the furthest away from (1, 1, 1) (which is
        in the middle of the face)
        """
        vertices = np.array(self._twin_form.facets[0].vertices)
        for i, vertex in enumerate(vertices):
            if np.allclose(vertex, [0, 0, 0]):
                vertices = np.delete(vertices, i, 0)
                break
        direction = np.array([1, 1, 1])
        angles = [get_angle(v, direction) for v in vertices]
        angles, ids = zip(*sorted(zip(angles, list(range(len(angles))))))
        return vertices[ids[-1]], vertices[ids[-2]]

    def _get_all_symmetry_operations(self) -> List[np.ndarray]:
        """
        Get the 60 icosahedral symmetry operations in the coordinate
        system defined by the particle as it is currently oriented.
        """
        fivefold_1, fivefold_2 = self._get_two_fivefold_axes()
        R1 = get_rotation_matrix(1 * 2 * np.pi / 5, fivefold_1)
        R2 = get_rotation_matrix(3 * 2 * np.pi / 5, fivefold_2)
        symmetries = [np.eye(3)]

        while len(symmetries) < 60:
            for S in symmetries:
                for R in [R1, R2]:
                    S_new = np.dot(R, S)
                    for S in symmetries:
                        if np.allclose(S_new, S):
                            break
                    else:
                        symmetries.append(S_new)
                        if len(symmetries) == 60:
                            break
        assert len(symmetries) == 60
        return symmetries

    def _get_symmetry_operations(self) -> List[np.ndarray]:
        """
        Construct the subset of symmetry operations that duplicates
        a single tetrahedron to all 20 tetrahedra.
        """
        fivefold_1, fivefold_2 = self._get_two_fivefold_axes()
        symmetries = []
        inversion = - np.eye(3)
        symmetries.append(inversion)
        down = get_rotation_matrix(2 * 2 * np.pi / 5, fivefold_1)
        symmetries.append(down)
        symmetries.append(np.dot(inversion, down))
        for i in range(1, 5):
            R = get_rotation_matrix(i * 2 * np.pi / 5, fivefold_2)
            symmetries.append(R)
            symmetries.append(np.dot(inversion, R))
            symmetries.append(np.dot(R, down))
            symmetries.append(np.dot(inversion, np.dot(R, down)))
        assert len(symmetries) == 19
        return symmetries

    def get_strain_energy(self, shear_modulus, poissons_ratio):
        """
        Return a strain energy as estimated with the formula provided in
        A. Howie and L. D. Marks in Phil. Mag. A **49**, 95 (1984)
        [HowMar84]_ (Eq. 23), which assumes an inhomogeneous strain in
        the particle.

        Warning
        -------
        This value is only approximate. If the icosahedron is
        heavily truncated, the returned strain energy may be highly
        inaccurate.

        Parameters
        ----------
        shear_modulus
            Shear modulus of the material
        poissons_ratio
            Poisson's ratio of the material
        """
        eps_I = 0.0615
        strain_energy_density = 2 * shear_modulus * eps_I ** 2 / 9
        strain_energy_density *= (1 + poissons_ratio) / (1 - poissons_ratio)
        return strain_energy_density * self.volume


def _get_unique_coordinates(atoms: Atoms,
                            symmetries: List[np.ndarray],
                            base_element: np.ndarray) -> List[np.ndarray]:
    """
    Duplicate atoms with a list of symmetries, but avoid putting
    atoms on top of each other.

    atoms
        Atoms object to duplicate
    symmetries
        List of symmetry elements to act on atoms with
    base_element
        An vector in Cartesian coordinates. If two symmetry
        elements carries this vector to the same position,
        one symmetry element will be skipped.

    Returns
    -------
    A list of Cartesian coordinates with new atomic positions,
    including the original ones.
    """
    unique_coordinates = []
    symmetrical_elements = []
    for R in symmetries:
        element = np.dot(R, base_element)
        if is_array_in_arrays(element, symmetrical_elements):
            continue
        else:
            symmetrical_elements.append(element)
        for atom in atoms:
            unique_coordinates.append(np.dot(R, atom.position))
    return unique_coordinates


def _get_icosahedral_scale_factor():
    k = (5 + np.sqrt(5)) / 8
    return np.sqrt(2 / (3 * k - 1))
