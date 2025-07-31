from typing import Tuple, List
from ase import Atoms
import numpy as np
from .core import BaseParticle
from .core.geometry import get_symmetries, get_standardized_structure
from .core.form import setup_forms


class SingleCrystal(BaseParticle):
    """
    A `SingleCrystal` object is a Wulff construction of a single
    crystalline particle, i.e., a standard Wulff construction.

    Parameters
    ----------
    surface_energies
        A dictionary with surface energies, where keys are
        Miller indices and values surface energies (per area)
        in a unit of choice, such as J/m^2.
    primitive_structure
        primitive cell to implicitly define the point group as
        well as the atomic structure used if an atomic structure
        is requested. By default, an Au FCC structure is used.
    natoms
        Together with `primitive_structure`, this parameter
        defines the volume of the particle. If an atomic structure
        is requested, the number of atoms will as closely as possible
        match this value.
    symprec
        Numerical tolerance for symmetry analysis, forwarded to spglib.
    tol
        Numerical tolerance parameter.
    symmetry_operations
        This parameter allows one to pass an explicit list of allowed
        symmetry operations. By default (``None``) the allowed symmetry
        operations are obtained from :attr:`primitive_structure`.

    Example
    -------
    The following example illustrates some possible uses of a
    `SingleCrystal` object::

        >>> from wulffpack import SingleCrystal
        >>> from ase.build import bulk
        >>> from ase.io import write
        >>> surface_energies = {(1, 1, 0): 1.0, (1, 0, 0): 1.08}
        >>> prim = bulk('W', a=3.16, crystalstructure='bcc')
        >>> particle = SingleCrystal(surface_energies, prim)
        >>> particle.view()
        >>> write('single_crystal.xyz', particle.atoms) # Writes atomic structure to file

    """

    def __init__(
            self,
            surface_energies: dict,
            primitive_structure: Atoms = None,
            natoms: int = 1000,
            symprec: float = 1e-5,
            tol: float = 1e-5,
            symmetry_operations: List[np.ndarray] = None,
    ):
        standardized_structure = get_standardized_structure(primitive_structure, symprec=symprec)
        if symmetry_operations is None:
            symmetries = get_symmetries(standardized_structure, symprec=symprec)
        else:
            if len(symmetry_operations) == 0:
                raise ValueError('You need to provide at least one symmetry operation.')
            symmetries = symmetry_operations
        forms = setup_forms(surface_energies,
                            standardized_structure.cell.T,
                            symmetries,
                            symmetries)
        super().__init__(forms=forms,
                         standardized_structure=standardized_structure,
                         natoms=natoms,
                         tol=tol)

    @property
    def atoms(self) -> Atoms:
        """
        Returns an ASE Atoms object
        """
        return self._get_atoms()

    def get_shifted_atoms(
            self,
            center_shift: Tuple[float, float, float] = None,
    ) -> Atoms:
        """
        Returns an ASE Atoms object where the center has been shifted
        from with respect to the standardized cells. This can, for
        example, allow creation of atomistic representations in which
        the center of the nanoparticle does not coincide with an atom.
        Thereby the space of possible atomistic representations increases
        and may make the returned number of atoms closer to the requested
        number.

        Parameters
        ----------
        center_shift
            Shift of center in Cartesian coordinates.
        """
        return self._get_atoms(center_shift=center_shift)
