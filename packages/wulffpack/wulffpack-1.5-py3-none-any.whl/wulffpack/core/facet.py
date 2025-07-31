from typing import List, Tuple, Union
import numpy as np
from .geometry import get_angle, get_tetrahedral_volume


class Facet(object):
    """
    A `Facet` carries information about a particular facet, i.e.,
    only one facet out of potentially several that are equivalent
    by symmetry.

    Parameters
    ----------
    normal
        The normal to the surface in Cartesian coordintes
    energy
        Surface energy (in units of energy per surface area)
    rotation
        Symmetry operation (acting on scaled coordinates) that
        carried an arbtriraily defined "parent facet" to this facet
    original_grain
        If True, this facet is part of an "original grain", i.e.,
        in the case of decahedron/icosahedron, it is part of
        the first created tetrahedron
    tol
        Numerical tolerance
    """

    def __init__(
            self,
            normal: Union[List[float], Tuple[float]],
            energy: float,
            symmetry: np.ndarray,
            original_grain: bool = True,
            tol: float = 1e-5
    ):
        self.normal = np.array(normal) / np.linalg.norm(normal)
        self.original_normal = self.normal.copy()
        self.energy = energy
        self.symmetries = [symmetry]
        self.vertices = []
        self.original_grain = original_grain
        self.original_vertices = []
        self.tol = tol

    def __str__(self) -> str:
        width = 42
        s = []
        s += ['{s:-^{n}}'.format(s=' Facet ', n=width)]
        flds = dict(normal='', original_normal='', energy='12.4f', original_grain='')
        for fld, fmt in flds.items():
            s += ['{fld:16} : {value:{fmt}}'.format(fld=fld, value=getattr(self, fld), fmt=fmt)]
        s += [f'{"symmetries":16} :']
        for k, v in enumerate(self.symmetries):
            s += [f'  {k:4} : {v[0]}']
            s += [f'  {"":4}   {v[1]}']
            s += [f'  {"":4}   {v[2]}']
        return '\n'.join(s)

    def _repr_html_(self) -> str:
        s = []
        s += ['<table border="1" class="dataframe"']
        s += [
            '<thead><tr><th style="text-align: left;">Property</th><th>Value</th></tr></thead>'
        ]
        s += ['<tbody>']
        flds = dict(normal='', original_normal='', energy='12.4f', original_grain='')
        for fld, fmt in flds.items():
            s += [
                f'<tr><td style="text-align: left">{fld:22}</td>'
                '<td>{value:{fmt}}</td><tr>'.format(value=getattr(self, fld), fmt=fmt)
            ]
        s += '<tr><td style="text-align: left">symmetries</td><tr>'
        for k, v in enumerate(self.symmetries):
            s += [f'<tr><td>{k}</td><td>{v[0]}<br>{v[1]}<br>{v[2]}</td></tr>']
        s += ['</tbody>']
        s += ['</table>']
        return ''.join(s)

    def add_vertex(self, vertex: Union[List, tuple]):
        """
        Add a vertex to the list of vertices. This function checks
        that there is not already such a vertex, to ensure that
        no vertex is duplicated. It is also checked that the vertex
        lies in the expected plane (as defined by the first vertex and
        the surface normal).

        Parameters
        ----------
        vertex
            The vertex in Cartesian coordinates
        """
        # Need to check that the vertex is not already added
        # (relevant if more than three planes cross at the
        # same point, such as in a non-truncated octahedron)
        for comp_vertex in self.vertices:
            if np.linalg.norm(vertex - comp_vertex) < self.tol:
                return None
        # Check that it is in the right plane
        if self.vertices:
            if abs(np.dot(vertex, self.normal) - self.distance_from_origin) > self.tol:
                raise ValueError('Vertex {} corresponding to facet with normal {} '
                                 'does not lie in the same plane '
                                 'as previously added vertices.'.format(vertex, self.normal))
        self.vertices.append(vertex)

    @property
    def distance_from_origin(self) -> float:
        """Returns the distance from the origin to the facet."""
        return np.dot(self.vertices[0], self.normal)

    def remove_redundant_vertices(self):
        """
        Remove any vertex which is midway between two other vertices.
        This would not work if the polygon were concave, but that is
        not allowed anyway.
        """
        to_pop = []
        for i, vertex_i in enumerate(self.vertices):
            for j, vertex_j in enumerate(self.vertices):
                if j <= i:
                    continue
                v1 = vertex_j - vertex_i
                for k, vertex_k in enumerate(self.vertices):
                    if k <= j:
                        continue
                    v2 = vertex_k - vertex_i
                    angleish = abs(get_angle(v2, v1)) / np.pi
                    if abs(angleish - round(angleish)) > self.tol / 100:
                        continue
                    # Then we have found three vertices on a line
                    # Now we need to remove the middle one
                    v3 = vertex_k - vertex_j
                    d1 = np.linalg.norm(v1)
                    d2 = np.linalg.norm(v2)
                    d3 = np.linalg.norm(v3)
                    _, indices = zip(
                        *sorted(zip([d1, d2, d3], list(range(3)))))
                    to_pop.append([k, j, i][indices[-1]])
        for i in reversed(sorted(set(to_pop))):
            self.vertices.pop(i)

    @property
    def ordered_vertices(self) -> List[np.ndarray]:
        """
        Returns the vertices ordered such that they enclose a polygon.
        The first/last vertex occurs twice.

        It is assumed (but not checked) that the coordinates lie in
        a plane and that they form a convex polygon.
        """
        # Find closest pairs by comparing angles between each triplet of
        # vertices
        best_pairs = []
        for i, vertex_i in enumerate(self.vertices):
            # Its closest neighbors are those with which the largest angle is
            # formed
            best_angle = 0
            for j, vertex_j in enumerate(self.vertices):
                if i == j:
                    continue
                for k, vertex_k in enumerate(self.vertices):
                    if k <= j or i == k:
                        continue
                    angle = get_angle(vertex_j - vertex_i, vertex_k - vertex_i)
                    if angle > best_angle:
                        best_angle = angle
                        neighbors = (j, k)
            for neighbor in neighbors:
                pair = tuple(sorted([i, neighbor]))
                if pair not in best_pairs:
                    best_pairs.append(pair)

        # Make a new list of vertices, now in order (as implicitly
        # defined by the pairs of nearest neighbors)
        ordered_vertices = [self.vertices[0]]
        current_vertex_index = 0
        while len(ordered_vertices) < len(self.vertices):
            for pair_index, pair in enumerate(best_pairs):
                if current_vertex_index in pair:
                    for new_vertex_index in pair:
                        if new_vertex_index != current_vertex_index:
                            ordered_vertices.append(
                                self.vertices[new_vertex_index])
                            break
                    best_pairs.pop(pair_index)
                    current_vertex_index = new_vertex_index
                    break
        ordered_vertices.append(self.vertices[0])
        return ordered_vertices

    @property
    def face_as_triangles(self) -> List[List[np.ndarray]]:
        """
        Given N 3D coordinates, ABCD...N, split them into triangles
        that do not overlap. Two of the vertices of each triangle
        will be vertices of the face, the third vertex will be
        the origin.
        """
        vertices = self.ordered_vertices[:-1]
        nvertices = len(vertices)
        center = np.mean(vertices, axis=0)  # Mid point

        # Standardize order because some applications
        # (such as threejs) expect that
        normal = np.cross(vertices[1] - center,
                          vertices[0] - center)
        reverse = (np.dot(normal, self.normal) > 0)

        # Construct all triangles
        triangles = []
        for i in range(0, len(vertices)):
            if reverse:
                triangle = [center,
                            vertices[(i + 1) % nvertices],
                            vertices[i]]
            else:
                triangle = [center,
                            vertices[i],
                            vertices[(i + 1) % nvertices]]
            triangles.append(triangle)
        assert len(triangles) == len(vertices)
        return triangles

    @property
    def area(self) -> float:
        """Returns the total area of the facet."""
        area = 0
        for triangle in self.face_as_triangles:
            v1 = triangle[1] - triangle[0]
            v2 = triangle[2] - triangle[0]
            area += np.linalg.norm(np.cross(v1, v2))
        return area / 2

    @property
    def surface_energy(self) -> float:
        """Returns the total surface energy of the facet."""
        return self.area * self.energy

    def get_volume(self, origin: Union[List, tuple] = None) -> float:
        """
        Calculate the volume formed by the pyramid having the face as
        its base and the specified origin as its tip.

        Parameters
        ----------
        origin : list of 3 ints
            The origin

        Returns
        -------
        The total volume
        """
        if origin is None:
            origin = np.array([0, 0, 0])
        else:
            origin = np.array(origin)

        volume = 0
        for triangle in self.face_as_triangles:
            volume += get_tetrahedral_volume(triangle, origin)
        return volume

    @property
    def perimeter_length(self) -> float:
        """Returns the length of the perimeter"""
        length = 0.0
        ordered_vertices = self.ordered_vertices
        for i, vertex in enumerate(ordered_vertices[1:]):
            length += np.linalg.norm(vertex - ordered_vertices[i])
        return length
