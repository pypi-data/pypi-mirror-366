from typing import Dict
import numpy as np
from ase import Atoms
from .core import BaseParticle
from .core.form import setup_forms
from .core.geometry import (get_standardized_structure,
                            get_symmetries,
                            get_angle,
                            get_rotation_matrix,
                            break_symmetry)


class Decahedron(BaseParticle):
    """
    A `Decahedron` object is a generalized Wulff construction
    of a decahedral particle.

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
    The following example illustrates some possible uses of a
    `Decahedron` object::

        >>> from wulffpack import Decahedron
        >>> from ase.build import bulk
        >>> from ase.io import write
        >>> surface_energies = {(1, 1, 1): 1.0, (1, 0, 0): 1.14}
        >>> prim = bulk('Au')
        >>> particle = Decahedron(surface_energies,
        ...                       twin_energy=0.03,
        ...                       primitive_structure=bulk('Au'))
        >>> particle.view()
        >>> write('decahedron.xyz', particle.atoms) # Writes atomic structure

    """

    def __init__(self,
                 surface_energies: Dict[tuple, float],
                 twin_energy: float,
                 primitive_structure: Atoms = None,
                 natoms: int = 1000,
                 symprec: float = 1e-5,
                 tol: float = 1e-5):
        standardized_structure = get_standardized_structure(primitive_structure, symprec)
        symmetries = get_symmetries(standardized_structure, symprec)
        if len(symmetries) < 48:
            raise ValueError('A decahedron can only be created with a '
                             'primitive structure that has cubic symmetry')

        twin_boundaries = [(-1, 1, 1), (1, -1, 1)]
        symmetry_axes = [(0, 0, 1), np.cross(*twin_boundaries)]
        inversion = [False, True]
        broken_symmetries = break_symmetry(symmetries, symmetry_axes, inversion)

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
                            twin_boundary=twin_boundaries[0])

        super().__init__(forms=forms,
                         standardized_structure=standardized_structure,
                         natoms=natoms,
                         ngrains=5,
                         volume_scale=_get_decahedral_scale_factor(),
                         tol=tol)

        # Duplicate a single tetrahedron to form a complete decahedron
        # with five tetrahedra

        # Rotate such that fivefold axis is aligned with z axis
        fivefold_vector = self.fivefold_axis_vector
        rotation_axis = np.cross(fivefold_vector, [0, 0, 1])
        angle = np.arccos(fivefold_vector[2] / np.linalg.norm(fivefold_vector))
        R = get_rotation_matrix(angle, rotation_axis)
        self.rotate_particle(R)

        # Translate such that fivefold axis in x, y = 0, 0.
        # Dangerous to use max and min in z because the particle
        # may be truncated such that are several with the same value.
        # Instead check which vertices are furthest away from the Ino face.
        vertices = np.array(self._twin_form.facets[0].vertices)
        # hard code because there may not be an Ino facet...
        direction = np.array([1, 1, 0])
        projections = [np.dot(v, direction) for v in vertices]
        projections, ids = zip(*sorted(zip(projections,
                                           list(range(len(projections))))))
        min_vertex = vertices[ids[0]]
        max_vertex = vertices[ids[1]]

        # Check that rotation did its job
        assert np.linalg.norm(max_vertex[:2] - min_vertex[:2]) < 1e-5
        translation = np.array([-min_vertex[0], -min_vertex[1],
                                -(min_vertex[2] + max_vertex[2]) / 2])
        self.translate_particle(translation)

        # Rotate such that Ino facet aligns with a Cartesian vector
        current = self._twin_form.facets[0].normal + self._twin_form.facets[1].normal
        assert abs(current[2]) < 1e-5
        target = (0, -1, 0)
        angle = get_angle(current, target)
        R = get_rotation_matrix(angle, [0, 0, 1])
        self.rotate_particle(R)

        # Back up the vertices in a separate list
        # (that list is useful if creating an Atoms object)
        for facet in self._yield_facets():
            facet.original_vertices = [vertex.copy() for vertex in facet.vertices]

        # Strain the particle to fill space
        scale = _get_decahedral_scale_factor()
        for facet in self._yield_facets():
            for i in range(len(facet.vertices)):
                facet.vertices[i][0] *= _get_decahedral_scale_factor()
            # Scale normal too
            facet.normal[1] *= scale
            facet.normal[2] *= scale
            facet.normal /= np.linalg.norm(facet.normal)

        # Make five grains
        rotations = []
        for i in range(1, 5):
            rotations.append(get_rotation_matrix(i * 2 * np.pi / 5, [0, 0, 1]))
        self._duplicate_particle(rotations)

    @property
    def atoms(self) -> Atoms:
        """
        Returns an ASE Atoms object
        """
        atoms = self._get_atoms()

        # We delete one atomic layer on a twin facet because we will
        # get it back when we make five grains.
        # But we need to save the atoms on the five-fold axis.
        # Begin with identifying the maximum projection on one of the
        # twin facets.
        max_projection = -1e9
        twin_direction = self._twin_form.facets[0].original_normal
        for atom in atoms:
            projection = np.dot(twin_direction, atom.position)
            if projection > max_projection:
                max_projection = projection
        # Now delete all atoms that are
        # close to the maximum projection
        fivefold_atoms = Atoms()
        twin_indices = []
        for atom in atoms:
            projection = np.dot(twin_direction, atom.position)
            if abs(projection - max_projection) < 1e-5:
                twin_indices.append(atom.index)
                if abs(atom.position[0]) < 1e-5 and abs(atom.position[1]) < 1e-5:
                    fivefold_atoms.append(atom)
        del atoms[twin_indices]

        # Increase the distance from the x=0 plane by 1.8 % for each atom
        for atom in atoms:
            atom.position[0] = atom.position[0] * _get_decahedral_scale_factor()

        # Make five grains
        rotations = []
        for i in range(1, 5):
            rotations.append(get_rotation_matrix(i * 2 * np.pi / 5, [0, 0, 1]))
        new_positions = []
        for R in rotations:
            for atom in atoms:
                new_positions.append(np.dot(R, atom.position))
        atoms += Atoms('{}{}'.format(self.standardized_structure[0].symbol,
                                     len(new_positions)),
                       positions=new_positions)
        atoms += fivefold_atoms

        return atoms

    @property
    def fivefold_axis_vector(self) -> np.ndarray:
        """
        Returns a vector pointing in the
        direction of the five-fold axis.
        """
        twins = self._twin_form.facets
        v = np.cross(twins[0].normal,
                     twins[1].normal)
        # Normalize
        v /= np.linalg.norm(v)
        return v

    def get_strain_energy(self, shear_modulus: float, poissons_ratio: float) -> float:
        """
        Return strain energy as estimated with the formula provided in
        A. Howie and L. D. Marks in Phil. Mag. A **49**, 95 (1984)
        [HowMar84]_ (Eq. 10), which assumes an inhomogeneous strain in
        the particle.

        Warning
        -------
        This value is only approximate. If the decahedron is
        heavily truncated, the returned strain energy may be highly
        inaccurate.

        Parameters
        ----------
        shear_modulus
            Shear modulus of the material
        poissons_ratio
            Poisson's ratio of the material
        """
        eps_D = 0.0205
        strain_energy_density = shear_modulus * eps_D ** 2 / 4
        strain_energy_density /= (1 - poissons_ratio)
        return strain_energy_density * self.volume

    @property
    def aspect_ratio(self) -> float:
        """
        Returns the aspect ratio of the decahedron, here defined as
        the ratio between the longest distance between two vertices
        projected on the fivefold axis versus the longest distance
        between two vertices projected on the plane perpendicular
        to the fivefold axis.
        """
        z_coords = []
        xy_coords = []
        for facet in self._yield_facets():
            for vertex in facet.vertices:
                z_coords.append(vertex[2])
                xy_coords.append(vertex[:2])

        # Longest distance between two points along z axis
        # (because the particle has been rotated so that
        # fivefold axis aligns with z)
        height = max(z_coords) - min(z_coords)

        # Find longest distance between two points in xy plane
        width = 0
        for i, xy_coord_i in enumerate(xy_coords):
            for xy_coord_j in xy_coords[i + 1:]:
                dist = ((xy_coord_i - xy_coord_j)**2).sum()
                if dist > width:
                    width = dist
        return height / width**0.5


def _get_decahedral_scale_factor() -> float:
    return np.sqrt(10 - 4 * np.sqrt(5))
