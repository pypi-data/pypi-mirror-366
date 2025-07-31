from typing import Dict, List, Tuple
import numpy as np
from ase import Atoms
from .facet import Facet
from .form import Form
from scipy.spatial import ConvexHull
from .geometry import is_array_in_arrays


class BaseParticle():
    """
    Base class for Wulff constructions, useful for systems of
    (almost) any symmetry.

    Parameters
    ----------
    forms
        List of forms belonging to the system at hand
    standardized_structure
        The structural unit implicitly carrying information about
        basis vectors etc.
    natoms
        Used as a target number of atoms if an atomistic structure
        is requested. Together with `standardized_structure`,
        `natoms` also defines the volume of the particle.
    ngrains
        If only a part of a complete particle is to be constructed,
        for example a fifth of a decahedron, this should be reflected
        by this parameter.
    volume_scale
        Decahedral and icosahedral particle need to be strained to
        fill space. With this parameter, the volume is scaled such
        that the volume of the particle is correct *after* this
        straining.
    tolerance
        Numerical tolerance
    """

    def __init__(self, forms: List[Form],
                 standardized_structure: Atoms,
                 natoms: int,
                 ngrains: int = 1,
                 volume_scale: int = 1.0,
                 tol: float = 1e-5):
        self._natoms = natoms
        self._standardized_structure = standardized_structure
        self._forms = forms
        self.tol = tol
        self._SMALL = 1e-12

        facets = list(self._yield_facets())
        if min(f.energy for f in facets) < 0:  # interface energy can be negative
            self._closest_vertices(facets)
        else:
            self._dual_wulff_shape(facets)

        # Remove vertices that are on the line between two other vertices
        # (relevant in the Winterbottom case and some corner cases)
        for facet in self._yield_facets():
            facet.remove_redundant_vertices()

        # Delete facets with less than three vertices
        to_pop = []
        for i, form in enumerate(self.forms):
            if len(form.facets[0].vertices) < 3:
                to_pop.append(i)
        for i in reversed(to_pop):
            self.forms.pop(i)

        # Scale everyting such that the volume matches the specified one
        target_volume = self.natoms * standardized_structure.get_volume() / \
            len(standardized_structure)
        scale_factor = (target_volume / (ngrains * self.volume * volume_scale)) ** (1 / 3)
        self._scale_size(scale_factor)

    def __str__(self) -> str:
        width = 38
        s = []
        name = self.__class__.__name__
        s += ['{s:-^{n}}'.format(s=f' {name} ', n=width)]
        flds = dict(volume='12.4f', area='12.4f',
                    surface_energy='12.2f', average_surface_energy='12.4f',
                    edge_length='12.4f', number_of_corners='12d')
        for fld, fmt in flds.items():
            s += ['{fld:22} : {value:{fmt}}'.format(fld=fld, value=getattr(self, fld), fmt=fmt)]
        s += ['facet_fractions        :']
        for k, v in self.facet_fractions.items():
            s += [f'  {str(k):20} : {v:12.6f}']
        return '\n'.join(s)

    def _repr_html_(self) -> str:
        s = []
        s += ['<table border="1" class="dataframe"']
        s += [
            '<thead><tr><th style="text-align: left;">Property</th><th>Value</th></tr></thead>'
        ]
        s += ['<tbody>']
        flds = dict(volume='12.4f', area='12.4f',
                    surface_energy='12.2f', average_surface_energy='12.4f',
                    edge_length='12.4f', number_of_corners='12d')
        for fld, fmt in flds.items():
            s += [
                f'<tr><td style="text-align: left">{fld:22}</td>'
                '<td>{value:{fmt}}</td><tr>'.format(value=getattr(self, fld), fmt=fmt)
            ]
        s += '<tr><td style="text-align: left">facet_fractions</td><tr>'
        for k, v in self.facet_fractions.items():
            s += [
                '<tr><td style="text-align: right">'
                f'{str(k):22}</td><td>{v:.6f}</td><tr>'
            ]
        s += ['</tbody>']
        s += ['</table>']
        return ''.join(s)

    def _closest_vertices(self, facets):
        """
        The closest vertex technique calculates all possible vertices and eliminates
        vertices outside of the Wulff shape.
        This works for negative interface energies.
        """
        # Calculate intersection point for all possible combinations of three facets
        facets.sort(key=lambda x: x.energy)  # compare with small energies first in inner loop
        for i, fi in enumerate(facets):
            ni = fi.normal
            for j, fj in enumerate(facets[:i]):
                nj = fj.normal
                if abs(abs(np.dot(ni, nj)) - 1) < self._SMALL:
                    continue  # skip parallel facets
                for fk in facets[:j]:
                    mat = np.vstack([ni, nj, fk.normal])
                    if np.linalg.det(mat) == 0:
                        continue  # skip singular matrices
                    vertex = np.dot(np.linalg.inv(mat), [fi.energy, fj.energy, fk.energy])

                    # check if vertex lies outside of Wulff shape
                    for fl in facets:
                        projection = np.dot(vertex, fl.normal)
                        if projection > fl.energy + self._SMALL:
                            break
                    else:  # i.e. loop does not break
                        for f in [fi, fj, fk]:
                            f.add_vertex(vertex.copy())

    def _dual_wulff_shape(self, facets):
        """
        The Wulff construction calculates the vertices of the dual,
        calculates the convex hull of those vertices using scipy's
        ConvexHull, and then converts the dual back to the Wulff
        shape.
        """
        # Calculate convex hull of dual vertices
        duals = []
        for facet in self._yield_facets():
            facet_points = facet.normal * facet.energy
            duals.append(facet_points / np.dot(facet_points, facet_points))
        hull = ConvexHull(duals)

        # Calculate vertices of dual again (i.e., back to Wulff shape)
        for i, j, k in hull.simplices:
            normal = np.cross(duals[j] - duals[i], duals[k] - duals[i])
            if np.linalg.norm(normal) < self._SMALL:
                continue  # Rare instances of duals on a line
            if np.isclose(np.dot(normal, facets[i].normal), 0):
                raise ValueError('The vertex after the calculation of the dual and the'
                                 ' original facet are orthogonal. This indicates that the'
                                 ' facets that are provided cannot form a closed shape.'
                                 ' Please review your input.')
            normal *= facets[i].energy / np.dot(normal, facets[i].normal)
            for facet_i in (i, j, k):
                facets[facet_i].add_vertex(normal.copy())

    def _scale_size(self, scale_factor: float):
        """
        Scale the size of the particle.

        Parameters
        ----------
        scale_factor
            Factor that all coordinates will be scaled with.
        """
        for facet in self._yield_facets():
            for i, _ in enumerate(facet.vertices):
                facet.vertices[i] *= scale_factor
            for i, _ in enumerate(facet.original_vertices):
                facet.original_vertices[i] *= scale_factor

    @property
    def natoms(self) -> List[int]:
        """
        The approximate number of atoms in the particle
        (implicitly defining the volume).
        """
        return self._natoms

    @natoms.setter
    def natoms(self, natoms: int):
        """
        Change the approximate number of atoms and thus the volume.
        """
        scale_factor = (natoms / self._natoms) ** (1 / 3.)
        self._scale_size(scale_factor)
        self._natoms = natoms

    @property
    def forms(self) -> List[Form]:
        """List of inequivalent forms for the particle"""
        return self._forms

    @property
    def standardized_structure(self) -> Atoms:
        """
        The standardized atomic structure that defines the geometry
        and thus the meaning of the Miller indices. Also forms the building
        blocks when `particle.atoms` is called.
        """
        return self._standardized_structure

    @property
    def _twin_form(self) -> Form:
        """Returns the twin form if there is one, otherwise None."""
        for form in self.forms:
            if form.parent_miller_indices == 'twin':
                return form
        return None

    def get_continuous_color_scheme(self,
                                    base_colors: dict = None,
                                    normalize: bool = False) -> dict:
        """
        Returns a dictionary with RGB colors for each form.
        The colors smoothly interpolate between three
        base colors, corresponding to (1, 1, 1), (1, 1, 0) and
        (1, 0, 0). Note that this is sensible primarily for
        cubic systems.

        Parameters
        ----------
        base_colors
            User chosen colors for one or several of (1, 1, 1),
            (1, 1, 0) and (1, 0, 0). To enforce, say, green
            (1, 1, 1), use ``base_colors={(1, 1, 1): 'g'}``
        normalize
            If True, the norm of the RGB vectors will be 1. Note
            that this may affect the ``base_colors`` too.
        """
        from matplotlib.colors import to_rgba

        # Adapt base_colors dictionary
        new_base_colors = {}
        if base_colors:
            for key in base_colors.keys():
                adapted_key = tuple(sorted(abs(i) for i in key))
                new_base_colors[adapted_key] = base_colors[key]

        # Make sure base_colors is complete
        default_colors = {(1, 1, 1): '#2980B9',
                          (0, 1, 1): '#E92866',
                          (0, 0, 1): '#FFE82C'}
        for key, color in default_colors.items():
            if key not in new_base_colors:
                new_base_colors[key] = color
        A = [(1, 1, 1), (0, 1, 1), (0, 0, 1)]
        base_color_matrix = np.array([to_rgba(new_base_colors[f])[:3] for f in A]).T

        # Normalize rows in A
        A = np.array([np.array(miller) / np.linalg.norm(miller) for miller in A]).T

        # Calculate color for each form
        colors = {}
        for form in self.forms:
            if type(form.parent_miller_indices) is not tuple:
                continue
            miller = np.array(sorted(abs(i) for i in form.parent_miller_indices))
            color = np.linalg.solve(A, miller)
            color /= np.linalg.norm(color)
            color = np.dot(base_color_matrix, color)
            if normalize:
                color /= np.linalg.norm(color)
            else:
                color = [min(1, c) for c in color]
            colors[form.parent_miller_indices] = color
        return colors

    def make_plot(self, ax, alpha: float = 0.85, linewidth: float = 0.3, colors: dict = None):
        """
        Plot a particle in an axis object. This function can be used to
        make customized plots of particles.

        Parameters
        ----------
        ax : matplotlib Axes3DSubplot
            An axis object with 3d projection
        alpha
            Opacity of the faces
        linewidth
            Thickness of lines between faces
        colors
            Allows custom colors for facets of all or a subset of forms,
            example `{(1, 1, 1): '#FF0000'}`

        Example
        -------
        In the following example, three different particles are
        plotted in the same figure::

            >>> from wulffpack import SingleCrystal, Decahedron, Icosahedron
            >>> import matplotlib.pyplot as plt
            >>> from mpl_toolkits.mplot3d import Axes3D
            >>>
            >>> surface_energies = {(1, 1, 1): 1.0,
            ...                     (1, 0, 0): 1.1,
            ...                     (1, 1, 0): 1.15,
            ...                     (3, 2, 1): 1.15}
            >>> twin_energy = 0.05
            >>>
            >>> fig = plt.figure(figsize=(3*4.0, 4.0))
            >>> ax = fig.add_subplot(131, projection='3d')
            >>> particle = SingleCrystal(surface_energies)
            >>> particle.make_plot(ax)
            >>>
            >>> ax = fig.add_subplot(132, projection='3d')
            >>> particle = Decahedron(surface_energies,
            ...                       twin_energy=0.05)
            >>> particle.make_plot(ax)
            >>>
            >>> ax = fig.add_subplot(133, projection='3d')
            >>> particle = Icosahedron(surface_energies,
            ...                        twin_energy=0.05)
            >>> particle.make_plot(ax)
            >>>
            >>> plt.subplots_adjust(top=1, bottom=0, left=0,
            ...                     right=1, wspace=0, hspace=0)
            >>> plt.savefig('particles.png')

        """
        from mpl_toolkits.mplot3d.art3d import (Poly3DCollection,
                                                Line3DCollection)

        # Standardize color dict
        if colors is None:
            colors = {}

        default_colors = ['#D62728',
                          '#E377C2',
                          '#8C564B',
                          '#7F7F7F',
                          '#9467BD',
                          '#BCBD22',
                          '#17BECF',
                          '#AEC7E8',
                          '#FFBB78',
                          '#98DF8A',
                          '#FF9896',
                          '#C5B0D5',
                          '#C49C94',
                          '#F7B6D2',
                          '#C7C7C7',
                          '#DBDB8D',
                          '#9EDAE5']

        mins = [1e9, 1e9, 1e9]
        maxs = [-1e9, -1e9, -1e9]
        poly3d = []

        used_forms = []
        color_counter = 0
        for form in self.forms:
            if form.parent_miller_indices == 'twin':
                continue

            # Determine color
            if form.parent_miller_indices in colors:
                color = colors[form.parent_miller_indices]
            elif form.parent_miller_indices == (1, 1, 1):
                color = '#4f81f1'
                colors[form.parent_miller_indices] = color
            elif tuple(sorted(form.parent_miller_indices)) == (0, 0, 1):
                color = '#f8c73b'
                colors[form.parent_miller_indices] = color
            elif tuple(sorted(form.parent_miller_indices)) == (0, 1, 1):
                color = '#2CA02C'
                colors[form.parent_miller_indices] = color
            else:
                color = default_colors[color_counter % len(default_colors)]
                colors[form.parent_miller_indices] = color
                color_counter += 1

            # Save the used forms to be able to make a legend
            # (the colors dict may contain forms that are not present
            # if it was supplied by the user)
            if form.parent_miller_indices not in used_forms:
                used_forms.append(form.parent_miller_indices)

            # Plot all facets in the form
            for facet in form.facets:
                poly3d = [facet.ordered_vertices]

                # Facets
                collection = Poly3DCollection(poly3d, alpha=alpha)
                collection.set_facecolor(color)
                ax.add_collection3d(collection)

                # Lines
                ax.add_collection3d(Line3DCollection(poly3d, colors='k', linewidths=linewidth))

                # Find proper ranges for the axes
                for vertex in facet.ordered_vertices:
                    for i, v in enumerate(vertex):
                        if v > maxs[i]:
                            maxs[i] = v
                        if v < mins[i]:
                            mins[i] = v

        # Plot fake lines to make a legend
        for form in used_forms:
            if isinstance(form, tuple):
                label = ('{{' + '{}' * len(form) + '}}').format(*form)
            else:
                label = form
            ax.plot([0, 0], [0, 0], color=colors[form], linewidth=8.0, label=label)

        # Fiddle with the layout
        extent = max(maxs) - min(mins)
        bounds = [min(mins) + 0.15 * extent, max(maxs) - 0.15 * extent]
        ax.set_xlim(*bounds)
        ax.set_ylim(*bounds)
        ax.set_zlim(*bounds)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        ax.axis('off')
        try:
            ax.set_box_aspect((1, 1, 1))
        except AttributeError:
            # set_box_aspect only available in recent versions of matplotlib
            pass

    def view(self, alpha: float = 0.85, linewidth: float = 0.3, colors: dict = None,
             legend: bool = True, save_as: str = None):
        """
        Use matplotlib to view a rendition of the particle.

        Parameters
        ----------
        alpha
            Opacity of the faces
        linewidth
            Thickness of lines between faces
        colors
            Allows custom colors for facets of all or a subset of forms,
            example `{(1, 1, 1): '#FF0000'}`
        legend
            Whether or not to show a legend with facet-color definitions
        save_as
            Filename to save figure as. If None, show the particle
            with the GUI instead.
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # NOQA
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        self.make_plot(ax, alpha=alpha, linewidth=linewidth, colors=colors)
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
        if legend:
            fig.legend(frameon=False)
        plt.axis('off')
        if save_as:
            plt.savefig(save_as, transparent=True)
        else:
            plt.show()

    def write(self, filename: str):
        """
        Write particle to file. The file format is derived from the
        filename. Currently supported fileformats are:

            * Wavefront .obj

        Parameters
        ---------
        filename
            Filename of file to write to
        """
        supported_file_formats = ['obj']
        fileformat = filename.split('.')[-1]
        if fileformat not in supported_file_formats:
            raise ValueError('File format {} not supported, '.format(fileformat) +
                             'supported formats are: ' + ' '.join(supported_file_formats))
        with open(filename, 'w') as f:
            if fileformat == 'obj':
                f.write('# Vertices\n')
                for form in self.forms:
                    for facet in form.facets:
                        for vertex in facet.ordered_vertices[:-1]:
                            f.write('v {:15.8f} {:15.8f} {:15.8f}\n'.format(*vertex))

                f.write('# Faces\n')
                vertex_counter = 1
                for form in self.forms:
                    # Define a group to be able to color each form separately
                    f.write('g {}\n'.format(form.parent_miller_indices))
                    for facet in form.facets:
                        # Tie the face to the right vertices. Count starts from 1.
                        s = ['{:5d}'.format(v + vertex_counter) for v in range(len(facet.vertices))]
                        vertex_counter += len(facet.vertices)
                        f.write('f ' + ' '.join(s) + '\n')

    def _yield_facets(self, only_original_grains: bool = False) -> Facet:
        """Generate all facets that are included in the facets dictionary."""
        for form in self.forms:
            for facet in form.facets:
                if only_original_grains and not facet.original_grain:
                    continue
                yield facet

    @property
    def volume(self) -> float:
        """Returns the volume of the particle"""
        volume = 0
        for form in self.forms:
            volume += form.volume
        return volume

    @property
    def area(self) -> float:
        """
        Returns total area of the surface of the particle (not including
        twin boundaries).
        """
        area = 0
        for form in self.forms:
            if form.parent_miller_indices != 'twin':
                area += form.area
        return area

    @property
    def edge_length(self) -> float:
        """Returns total edge length of the particle."""
        edge_length = 0
        for form in self.forms:
            if form.parent_miller_indices != 'twin':
                edge_length += form.edge_length / 2  # Every edge comes twice
        return edge_length

    @property
    def number_of_corners(self) -> float:
        """Returns the number of corners (vertices) on the particle."""
        unique_vertices = []
        for form in self.forms:
            if form.parent_miller_indices == 'twin':
                continue
            for facet in form.facets:
                for vertex in facet.vertices:
                    if not is_array_in_arrays(vertex, unique_vertices):
                        unique_vertices.append(vertex)
        return len(unique_vertices)

    @property
    def surface_energy(self) -> float:
        """
        The total surface energy of the particle (including twin boundaries).
        """
        E = 0
        for form in self.forms:
            E += form.surface_energy
        return E

    @property
    def facets(self) -> List[Facet]:
        """The facets of the particle (read-only).
        """
        return list(self._yield_facets())

    @property
    def facet_fractions(self) -> Dict[tuple, float]:
        """
        Returns a dict specifying fraction of each form
        (not including twin boundaries).
        """
        facet_fractions = {}
        total_area = 0
        for form in self.forms:
            if form.parent_miller_indices == 'twin':
                continue
            area = form.area
            total_area += area
            facet_fractions[form.parent_miller_indices] = facet_fractions.get(
                form.parent_miller_indices, 0) + area
        for form in facet_fractions:
            facet_fractions[form] = facet_fractions[form] / total_area
        return facet_fractions

    @property
    def average_surface_energy(self) -> float:
        """
        Average surface energy for the Wulff construction, i.e.,
        a weighted average over all the facets, where the weights are
        the area fraction of each facet.
        """
        fractions = self.facet_fractions
        weighted_average = 0
        used_miller_indices = []
        for form in self.forms:
            if form.parent_miller_indices == 'twin' or \
                    form.parent_miller_indices in used_miller_indices:
                continue
            weighted_average += form.energy * fractions[form.parent_miller_indices]
            used_miller_indices.append(form.parent_miller_indices)
        return weighted_average

    def _duplicate_particle(self, symmetries):
        """
        Duplicate the particle by applying symmetry operations.

        Useful for making an icosahedron from a single tetrahedron for example.

        Parameters
        ----------
        symmetries: list of NumPy arrays
            Each array a symmetry operation(operating on Cartesian coordinates)
            that should create a duplicate.
        """
        for form in self.forms:
            new_facets = []
            for facet in form.facets:
                for R in symmetries:
                    new_facet = Facet(normal=np.dot(R, facet.normal),
                                      energy=facet.energy,
                                      symmetry=None,
                                      original_grain=False)
                    for vertex in facet.vertices:
                        new_facet.add_vertex(np.dot(R, vertex))

                    new_facets.append(new_facet)
            for facet in new_facets:
                form.facets.append(facet)

    def translate_particle(self, translation: np.ndarray):
        """
        Translate the particle.

        Parameters
        ----------
        translation: list of 3 floats
            Translation vector
        """
        for facet in self._yield_facets():
            for i, vertex in enumerate(facet.vertices):
                facet.vertices[i] = vertex + translation

    def rotate_particle(self, rotation: np.ndarray):
        """
        Rotate the particle.

        Parameters
        ----------
        rotation
            Rotation matrix
        """
        if abs(abs(np.linalg.det(rotation)) - 1.0) > self.tol:
            raise ValueError('Provided matrix is not a rotation matrix '
                             '(its determinant does not equal 1 or -1).')
        for facet in self._yield_facets():
            for i, vertex in enumerate(facet.vertices):
                facet.vertices[i] = np.dot(rotation, vertex)
            facet.normal = np.dot(rotation, facet.normal)
            facet.original_normal = np.dot(rotation, facet.original_normal)
        self.standardized_structure.cell = np.dot(rotation, self.standardized_structure.cell.T).T
        for atom in self.standardized_structure:
            atom.position = np.dot(rotation, atom.position)

    def _get_atoms(self, center_shift: Tuple[float, float, float] = None) -> Atoms:
        """
        Returns an ASE Atoms object the atoms of which are all
        within the facets. In polycrystalline particles, only
        one grain will be returned.

        Parameters
        ----------
        center_shift
            Shift of center in Cartesian coordinates.
        """
        # Find max and min in x, y and z to bound the volume
        # where there may be atoms
        # (using scaled coordinates relative to the origin)
        mins = [1e9, 1e9, 1e9]
        maxs = [-1e9, -1e9, -1e9]
        for facet in self._yield_facets(only_original_grains=True):
            if facet.original_vertices:
                vertices = facet.original_vertices
            else:
                vertices = facet.vertices
            for vertex in vertices:
                scaled_vertex = np.linalg.solve(self.standardized_structure.cell.T, vertex)
                for i, v in enumerate(scaled_vertex):
                    if v < mins[i]:
                        mins[i] = v
                    if v > maxs[i]:
                        maxs[i] = v

        # Prepare an unnecessarily large atoms object
        mins = [int(i) - 1 for i in mins]
        maxs = [int(np.ceil(i)) + 1 for i in maxs]
        repeat = [int(np.ceil(i)) - int(j) for i, j in zip(maxs, mins)]
        atoms = self.standardized_structure.repeat(repeat)
        atoms.translate(np.dot(self.standardized_structure.cell.T, mins))

        if center_shift:
            atoms.translate(center_shift)

        # Loop over all scaled coordinates and check whether
        # they are within all facets
        to_delete = []
        for atom in atoms:
            for facet in self._yield_facets(only_original_grains=True):
                if np.dot(atom.position, facet.original_normal) > \
                        facet.distance_from_origin + 1e-5:
                    to_delete.append(atom.index)
                    break
        del atoms[to_delete]
        atoms.set_pbc(False)
        atoms.set_cell([0., 0., 0.])
        return atoms
