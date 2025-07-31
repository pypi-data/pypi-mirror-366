from typing import List
import numpy as np
from ase import Atoms
from ase.build import bulk
from spglib import get_symmetry_dataset, standardize_cell


def get_tetrahedral_volume(triangle, origin):
    """
    Get the volume of the tetrahedron formed by the origin
    and three vertices defined by the input.

    Parameters
    ----------
    triangle : list of list of 3 floats
        Three coordinates forming a triangle
    origin : list of 3 floats
        The origin

    Returns
    -------
    float
        The volume
    """
    if len(triangle) != 3:
        raise ValueError('triangle argument must contain three coordinates')
    M = np.vstack((triangle, [0, 0, 0]))
    M = np.vstack((M.transpose(), [1, 1, 1, 1]))
    return abs(np.linalg.det(M)) / 6


def get_angle(v1, v2, tol=1e-5):
    cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    if abs(abs(cos) - 1) < tol:
        if cos < -1.0:
            cos = -1.0
        elif cos > 1.0:
            cos = 1.0
    return np.arccos(cos)


def get_rotation_matrix(theta, u):
    u /= np.linalg.norm(u)
    R = np.zeros((3, 3))
    R[0, 0] = np.cos(theta) + u[0] * u[0] * (1 - np.cos(theta))
    R[1, 0] = u[0] * u[1] * (1 - np.cos(theta)) + u[2] * np.sin(theta)
    R[2, 0] = u[0] * u[2] * (1 - np.cos(theta)) - u[1] * np.sin(theta)
    R[0, 1] = u[0] * u[1] * (1 - np.cos(theta)) - u[2] * np.sin(theta)
    R[1, 1] = np.cos(theta) + u[1] * u[1] * (1 - np.cos(theta))
    R[2, 1] = u[1] * u[2] * (1 - np.cos(theta)) + u[0] * np.sin(theta)
    R[0, 2] = u[0] * u[2] * (1 - np.cos(theta)) + u[1] * np.sin(theta)
    R[1, 2] = u[1] * u[2] * (1 - np.cos(theta)) - u[0] * np.sin(theta)
    R[2, 2] = np.cos(theta) + u[2] * u[2] * (1 - np.cos(theta))
    return R


def get_standardized_structure(structure: Atoms = None, symprec: float = 1e-5) -> Atoms:
    """
    Returns a standardized structure based on a primitive one,
    using the spglib routine `standardize_cell`.

    Parameters
    ----------
    structure
        Structure that should be standardized. If None,
        FCC Au with lattice parameter 4.0 is returned.
    symprec
        Numerical tolerance for symmetry analysis, forwarded to spglib.
    """
    if structure is None:
        structure = bulk('Au', crystalstructure='fcc', a=4.0)

    spg_structure = (
        structure.get_cell(),
        structure.get_scaled_positions(),
        structure.get_atomic_numbers(),
    )
    cell, scaled_positions, atomic_numbers = standardize_cell(spg_structure, symprec=symprec)
    return Atoms(atomic_numbers,
                 scaled_positions=scaled_positions,
                 cell=cell,
                 pbc=True)


def break_symmetry(full_symmetry: List[np.ndarray],
                   symmetry_axes: List[np.ndarray],
                   inversion: List[bool] = None) -> List[np.ndarray]:
    """
    Reduce symmetry elements to only those that do not affect
    one or more vectors.

    Parameters
    ----------
    full_symmetry
        List of candidate symmetries
    symmetry_axes
        Vectors that must remain unchanged by symmetry operation
    inversion
        One boolean for each `symmetry_axis`, if True, a symmetry
        element is kept if it only inverts any or all of the
        symmetry axes
    """
    if inversion is None:
        inversion = [False] * len(symmetry_axes)
    else:
        if len(inversion) != len(symmetry_axes):
            raise ValueError('inversion must be a list of bools with '
                             'the same length as symmetry_axes '
                             '({} != {})'.format(len(inversion),
                                                 len(symmetry_axes)))
    broken_symmetry = []
    for R in full_symmetry:
        for symmetry_axis, inv in zip(symmetry_axes, inversion):
            v = np.dot(R, symmetry_axis)
            if not np.allclose(v, symmetry_axis):
                if inv:
                    if not np.allclose(v, -symmetry_axis):
                        break
                else:
                    break
        else:
            broken_symmetry.append(R)
    return broken_symmetry


def get_symmetries(structure: Atoms, symprec: float = 1e-5) -> (Atoms, List[np.ndarray]):
    """
    Get symmetry operations of the point group.

    Parameters
    ----------
    structure
        The structure for which the symmetry operations
        is to be extracted
    symprec
        Numerical tolerance for symmetry analysis, forwarded to spglib.

    Returns
    -------
    list of NumPy arrays
        The symmetry operations of the point group in matrix format.
    """

    spg_structure = (
        structure.get_cell(),
        structure.get_scaled_positions(),
        structure.get_atomic_numbers(),
    )
    symmetry_data = get_symmetry_dataset(spg_structure, symprec=symprec)
    rotations = []
    for R in symmetry_data.rotations:
        if not is_array_in_arrays(R, rotations):
            rotations.append(R)
    return rotations


def is_array_in_arrays(array: np.ndarray, arrays: List[np.ndarray]) -> bool:
    """
    Checks whether an array exists (True) or not (False) in a list
    of arrays.

    Parameters
    ----------
    array
        Array to be searched for
    arrays
        List of arrays to search among
    """
    for array_comp in arrays:
        if np.allclose(array, array_comp):
            return True
    return False


def where_is_array_in_arrays(array: np.ndarray, arrays: List[np.ndarray]) -> int:
    """
    Returns the index of an array in a list of arrays.

    array
        Array to search for
    arrays
        List of arrays to search within
    """
    for i, array_comp in enumerate(arrays):
        if np.allclose(array, array_comp):
            return i
    return -1
