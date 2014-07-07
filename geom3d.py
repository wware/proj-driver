#!/usr/bin/env python

"""
Usage:
  CMD (-T | --test) [-v | --verbose]
"""

import docopt
import sys

# Floating point madness
WIGGLE_ROOM = 1.0e-10

def sign(x):
    """
    >>> sign(1.0e-10)
    True
    >>> sign(1)
    True
    >>> sign(1.0e10)
    True
    >>> sign(-1.0e-10)
    False
    >>> sign(-1)
    False
    >>> sign(-1.0e10)
    False
    """
    return x > 0.0


class Vector(object):

    def __init__(self, x, y=None, z=None):
        """
        >>> v = Vector(1, 2, 3)
        >>> v.x
        1
        >>> v.y
        2
        >>> v.z
        3
        >>> v = Vector((3.1416, 6.2832, 1.41421))
        >>> v.x
        3.1416
        >>> v.y
        6.2832
        >>> v.z
        1.41421
        """
        if y is None:
            self.x, self.y, self.z = x
        else:
            self.x, self.y, self.z = x, y, z

    def __repr__(self):
        """
        >>> v = Vector(1.2, 3.4, 5.6)
        >>> v
        <1.2,3.4,5.6>
        """
        return "<{0},{1},{2}>".format(self.x, self.y, self.z)

    def dot(self, v):
        """
        >>> v = Vector(1, 2, 3)
        >>> v.dot(Vector(4, 5, 6))
        32
        """
        return self.x * v.x + self.y * v.y + self.z * v.z

    def __eq__(self, v):
        """
        This is necessary because floating-point arithmetic is imperfect.
        >>> Vector(1.0, 2.0, 3.0) == Vector(1.00000000001, 1.999999999999, 3.0)
        True
        >>> Vector(1.0, 2.0, 3.0) == Vector(1.00001, 1.9999, 3.0)
        False
        """
        return abs(self.diff(v)) < WIGGLE_ROOM

    def __abs__(self):
        """
        >>> v = Vector(1, 2, 3)
        >>> expected = (1 + 4 + 9) ** .5
        >>> abs(v) == expected
        True
        """
        return (self.dot(self)) ** .5

    def scale(self, k):
        """
        >>> Vector(1, 2, 3).scale(2)
        <2,4,6>
        """
        return Vector(k * self.x, k * self.y, k * self.z)

    def unit_length(self):
        """
        >>> p = (1./3) ** .5
        >>> v = Vector(1, 1, 1).unit_length()
        >>> v == Vector(p, p, p)
        True
        """
        return self.scale(1.0 / abs(self))

    def cross(self, v):
        """
        >>> v = Vector(1, 2, 3)
        >>> v.cross(Vector(4, 5, 6))
        <-3,6,-3>
        """
        ux, uy, uz = self.x, self.y, self.z
        vx, vy, vz = v.x, v.y, v.z
        return Vector(uy * vz - uz * vy,
                      uz * vx - ux * vz,
                      ux * vy - uy * vx)

    def add(self, v):
        """
        >>> v = Vector(4, 6, 8)
        >>> v.add(Vector(1, 2, 3))
        <5,8,11>
        """
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z)

    def diff(self, v):
        """
        >>> v = Vector(4, 6, 8)
        >>> v.diff(Vector(1, 2, 3))
        <3,4,5>
        """
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)


class BBox:
    def __init__(self, v1=None, v2=None):
        """
        >>> bbox = BBox(Vector(0, 0, 0), Vector(1, 1, 1))
        >>> bbox._min
        <0,0,0>
        >>> bbox._max
        <1,1,1>
        """
        if v1 is not None:
            assert v2 is not None
            assert v1.x <= v2.x
            assert v1.y <= v2.y
            assert v1.z <= v2.z
            self._min, self._max = v1, v2
            def contains_x(x, x1=v1.x-WIGGLE_ROOM, x2=v2.x+WIGGLE_ROOM):
                return x1 < x < x2
            def contains_y(y, y1=v1.y-WIGGLE_ROOM, y2=v2.y+WIGGLE_ROOM):
                return y1 < y < y2
            def contains_z(z, z1=v1.z-WIGGLE_ROOM, z2=v2.z+WIGGLE_ROOM):
                return z1 < z < z2
            def contains_yz(y, z, y1=v1.y-WIGGLE_ROOM, y2=v2.y+WIGGLE_ROOM,
                            z1=v1.z-WIGGLE_ROOM, z2=v2.z+WIGGLE_ROOM):
                return y1 < y < y2 and z1 < z < z2
        else:
            self._min = self._max = None
            def contains_x(x):
                return False
            def contains_y(y):
                return False
            def contains_z(z):
                return False
            def contains_yz(y, z):
                return False
        self.contains_x = contains_x
        self.contains_y = contains_y
        self.contains_z = contains_z
        self.contains_yz = contains_yz

    def __contains__(self, vector):
        """
        >>> bbox = BBox(Vector(0, 0, 0), Vector(1, 1, 1))
        >>> Vector(0.5, 0.5, 0.5) in bbox
        True
        >>> Vector(0.5, 0.5, 1.1) in bbox
        False
        """
        return self.contains_x(vector.x) and \
            self.contains_y(vector.y) and \
            self.contains_z(vector.z)

    def __repr__(self):
        return '<BBox {0} {1}>'.format(self._min, self._max)

    def copy(self):
        """
        >>> bbox1 = BBox(Vector(1, 2, 3), Vector(4, 5, 6))
        >>> bbox2 = bbox1.copy()
        >>> bbox1._max = Vector(7, 8, 9)
        >>> bbox1
        <BBox <1,2,3> <7,8,9>>
        >>> bbox2
        <BBox <1,2,3> <4,5,6>>
        """
        return BBox(self._min, self._max)

    def size(self):
        """
        >>> bbox = BBox(Vector(0, -1, 0), Vector(1, 1, 3))
        >>> bbox.size()
        <1,2,3>
        """
        return self._max.diff(self._min)

    def set_size(self, u):
        """
        >>> bbox = BBox(Vector(0, 0, 0), Vector(1, 1, 1))
        >>> bbox.set_size(Vector(2, 3, 4))
        >>> bbox
        <BBox <-0.5,-1.0,-1.5> <1.5,2.0,2.5>>
        """
        v = u.diff(self.size()).scale(0.5)
        assert v.x >= 0
        assert v.y >= 0
        assert v.z >= 0
        self._min = self._min.diff(v)
        self._max = self._max.add(v)

    def expand(self, other):
        if self._min is None:
            return other
        elif other._min is None:
            return self
        return BBox(Vector(min(self._min.x, other._min.x),
                           min(self._min.y, other._min.y),
                           min(self._min.z, other._min.z)),
                    Vector(max(self._max.x, other._max.x),
                           max(self._max.y, other._max.y),
                           max(self._max.z, other._max.z)))

    def _iterator(self, xmin, xmax, xsteps):
        """
        >>> g = BBox()
        >>> [x for x in g._iterator(1, 10, 4)]
        [1.0, 4.0, 7.0, 10.0]
        >>> [x for x in g._iterator(-10, -1, 4)]
        [-10.0, -7.0, -4.0, -1.0]
        """
        assert xmax >= xmin
        dx = (1.0 * xmax - xmin) / (xsteps - 1)
        x = 1.0 * xmin
        for i in range(xsteps):
            yield x
            x += dx

    def getXiterator(self, xsteps):
        """
        >>> bb = BBox(Vector(0.0, 0.0, 1.0), Vector(1.0, 2.0, 4.0))
        >>> [x for x in bb.getXiterator(5)]
        [0.0, 0.25, 0.5, 0.75, 1.0]
        >>> [x for x in bb.getXiterator(5)]
        [0.0, 0.25, 0.5, 0.75, 1.0]
        """
        return self._iterator(self._min.x, self._max.x, xsteps)

    def getYiterator(self, ysteps):
        """
        >>> bb = BBox(Vector(0.0, 0.0, 1.0), Vector(1.0, 2.0, 4.0))
        >>> [y for y in bb.getYiterator(9)]
        [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        >>> [y for y in bb.getYiterator(9)]
        [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        """
        return self._iterator(self._min.y, self._max.y, ysteps)

    def getZiterator(self, zsteps):
        """
        >>> bb = BBox(Vector(0.0, 0.0, 1.0), Vector(1.0, 2.0, 4.0))
        >>> [z for z in bb.getZiterator(7)]
        [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        >>> [z for z in bb.getZiterator(7)]
        [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        """
        return self._iterator(self._min.z, self._max.z, zsteps)


class Triangle:
    """
    >>> t = Triangle(
    ...     Vector(-20, -15, 0.0),
    ...     Vector(-20, -15, 20.0),
    ...     Vector(-20, -9.0, 0.0),
    ...     Vector(-1.0, 0.0, 0.0)
    ... )
    >>> t.vertices
    (<-20,-15,0.0>, <-20,-15,20.0>, <-20,-9.0,0.0>)
    >>> t.normal
    <-1.0,0.0,0.0>

    >>> t = Triangle(
    ...     Vector(-20, -15, 0.0),
    ...     Vector(-20, -15, 20.0),
    ...     Vector(-20, -9.0, 0.0)
    ... )
    >>> t.vertices
    (<-20,-15,0.0>, <-20,-15,20.0>, <-20,-9.0,0.0>)
    >>> t.normal
    <-1.0,0.0,0.0>

    >>> Vector(-20, -12, 5.0) in t
    True
    >>> Vector(-20, -16, 5.0) in t
    False
    >>> Vector(-20, -12, 20.0) in t
    False

    Test if it's out of plane
    >>> Vector(-20.0001, -12, 5.0) in t
    False
    """
    def __init__(self, vertex1, vertex2, vertex3, normal=None):
        if normal is None or normal == Vector(0, 0, 0):
            # Replace normal with right-hand-rule-generated unit vector
            u = vertex2.diff(vertex1)
            v = vertex3.diff(vertex2)
            normal = u.cross(v).unit_length()
        self.vertices = (vertex1, vertex2, vertex3)
        self.normal = normal

        minx = min(vertex1.x, vertex2.x, vertex3.x)
        miny = min(vertex1.y, vertex2.y, vertex3.y)
        minz = min(vertex1.z, vertex2.z, vertex3.z)
        maxx = max(vertex1.x, vertex2.x, vertex3.x)
        maxy = max(vertex1.y, vertex2.y, vertex3.y)
        maxz = max(vertex1.z, vertex2.z, vertex3.z)

        self._bbox = bbox = \
            BBox(Vector(minx, miny, minz), Vector(maxx, maxy, maxz))

        # this number is the same for any point in the triangle
        self.k = k = normal.dot(vertex1)

        def interior(p,
                     k=k,
                     sign=sign,
                     vertex1=vertex1,
                     vertex2=vertex2,
                     vertex3=vertex3,
                     normal=normal,
                     diff1=vertex2.diff(vertex1),
                     diff2=vertex3.diff(vertex2),
                     diff3=vertex1.diff(vertex3)):
            return (abs(normal.dot(p) - k) < WIGGLE_ROOM) and [
                sign(normal.dot(diff1.cross(p.diff(vertex1)))),
                sign(normal.dot(diff2.cross(p.diff(vertex2)))),
                sign(normal.dot(diff3.cross(p.diff(vertex3))))
            ] in ([True, True, True], [False, False, False])
        self.__contains__ = interior

        def bbox_contains_yz(y, z, f=bbox.contains_yz):
            return f(y, z)
        self.bbox_contains_yz = bbox_contains_yz

    def __repr__(self):
        vecs = (self.normal,) + self.vertices
        return '<n:{0}\n    {1}\n    {2}\n    {3}>'.format(*vecs)

    def __eq__(self, other):
        return self.normal == other.normal and self.vertices == other.vertices

    def intersect(self, y, z):
        """
        For given values of y and z, figure out where this triangle intersects
        a line parallel to the x axis at those y and z values, and return the
        x-coordinate of the intersection and the sign of the normal vector in
        the x direction. If the triangle doesn't intersect that line, or if the
        normal vector is perpendicular to the x axis, return None.

        >>> t = Triangle(
        ...     Vector(1.0, 1.0, 0.0),
        ...     Vector(1.0, 0.0, 0.0),
        ...     Vector(1.0, 0.0, 1.0)
        ... )
        >>> t.intersect(0.4, 0.4)
        (<1.0,0.4,0.4>, <-1.0,0.0,0.0>)
        >>> t.intersect(0.6, 0.6)
        >>> t = Triangle(
        ...     Vector(1.0, 0.0, 0.0),
        ...     Vector(0.0, 1.0, 0.0),
        ...     Vector(0.0, 0.0, 1.0)
        ... )
        >>> t.intersect(0.00001, 0.00001)
        (<0.99998,1e-05,1e-05>, <...>)
        >>> t.intersect(0.2, 0.2)
        (<0.6,0.2,0.2>, <...>)
        >>> t.intersect(0.4, 0.4)
        (<0.2,0.4,0.4>, <...>)
        >>> t.intersect(0.6, 0.6)

        >>> A = Vector(0, 0, 0)
        >>> C = Vector(0, 1, 0)
        >>> D = Vector(0, 0, 1)
        >>> t = Triangle(A, D, C)
        >>> t.intersect(0.25, 0.25)
        (<-0.0,0.25,0.25>, <-1.0,0.0,0.0>)
        """
        normal = self.normal
        nx = normal.x
        if nx == 0.0:
            return None

        # find intersection
        point = Vector((self.k - normal.y * y - normal.z * z) / nx, y, z)
        if point not in self._bbox:
            return None

        if point in self:
            return (point, normal)
        else:
            return None


def main():
    args = docopt.docopt(__doc__.replace('CMD', sys.argv[0]))

    if args['-T'] or args['--test']:
        import doctest
        verbose = args['-v'] or args['--verbose']
        failure_count, _ = doctest.testmod(verbose=verbose,
                                           optionflags=doctest.ELLIPSIS)
        sys.exit(failure_count)


if __name__ == '__main__':
    main()
