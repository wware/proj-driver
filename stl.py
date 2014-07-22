#!/usr/bin/env python

"""
Usage:
  CMD -z <ZVALUE>  [--red | -r] -f <filename> [-p | --profile]
  CMD (-T | --test) [-v | --verbose]

Example:
  ./stl.py -z 4 -f example.stl > example.rgb
  convert -size 1024x768 -alpha off -depth 8 example.rgb example-0004.png
"""

import docopt
import string
import struct
import sys
import types
from geom3d import Triangle, BBox, Vector


class Stl:
    def __init__(self, *args):
        if type(args[0]) in (types.StringType, types.UnicodeType):
            self.filename = args[0]
            self.triangles = []
            inf = open(self.filename)
            triangleList = self.from_input_file(inf)
        else:
            self.filename = self.preamble = None
            triangleList = args
        self.triangles = triangleList
        bb = BBox()
        for tri in triangleList:
            bb = bb.expand(tri._bbox)
        self._bbox = bb

    def from_input_file(self, inf):
        """
        TODO Handle the ASCII STL format
        """
        R = inf.read()
        self.preamble = ''.join(filter(lambda ch: ch != '\0', list(R[:80])))
        R = R[80:]
        numTriangles, R = struct.unpack('I', R[:4])[0], R[4:]
        triangleList = []
        for i in range(numTriangles):
            tri, R = self.triangle_from_string(R)
            triangleList.append(tri)
        return triangleList

    @classmethod
    def triangle_from_string(cls, str):
        """
        >>> t, str = Stl.triangle_from_string(
        ...     "\\x00\\x00\\x80\\xbf" +   # normal
        ...     "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00" +
        ...     "\\x0c\\x02\\xa0\\xc1" +   # vertex1
        ...     "\\x58\\x39\\x72\\xc1\\x00\\x00\\x00\\x00" +
        ...     "\\x0c\\x02\\xa0\\xc1" +   # vertex2
        ...     "\\x58\\x39\\x72\\xc1\\x00\\x00\\xa0\\x41" +
        ...     "\\x0c\\x02\\xa0\\xc1" +   # vertex3
        ...     "\\x00\\x00\\x10\\xc1\\x00\\x00\\x00\\x00" +
        ...     "\\x12\\x34"    # don't care
        ... )
        >>> len(str)
        0
        >>> n, v = t.normal, t.vertices
        >>> len(v)
        3
        >>> t.normal
        <-1.0,0.0,0.0>
        >>> t.vertices[0]
        <-20.0009994507,-15.138999939,0.0>
        >>> t.vertices[1]
        <-20.0009994507,-15.138999939,20.0>
        >>> t.vertices[2]
        <-20.0009994507,-9.0,0.0>
        """
        assert len(str) >= 50
        bytes, str = str[:50], str[50:]
        coords = struct.unpack('ffffffffffffH', bytes)
        normal = Vector(coords[:3])
        vertex1 = Vector(coords[3:6])
        vertex2 = Vector(coords[6:9])
        vertex3 = Vector(coords[9:12])
        t = Triangle(vertex1, vertex2, vertex3, normal)
        return (t, str)

    def bbox(self):
        return self._bbox

    def __repr__(self):
        return '<Stl "{0}" {1} triangles>'.format(self.filename,
                                                  len(self.triangles))

    def dump(self):
        r = repr(self) + '\n'
        for t in self.triangles:
            r += repr(t) + '\n'
        return r[:-1]

    def getPointList(self, y, z):
        """
        It would be more efficient to pre-sort the triangles into
        coarse (y,z) buckets and use those buckets to filter a smaller
        set of triangles. But I don't need that efficiency yet and
        likely that would be a bit of work.
        >>> A = Vector(0, 0, 0)
        >>> B = Vector(1, 0, 0)
        >>> C = Vector(0, 1, 0)
        >>> D = Vector(0, 0, 1)
        >>> stl = Stl(Triangle(A, B, D),
        ...           Triangle(A, C, B),
        ...           Triangle(A, D, C),
        ...           Triangle(B, C, D))
        >>> stl.getPointList(2, 2)
        []
        >>> stl.getPointList(1, 1)
        []
        >>> stl.getPointList(0.5, 0.5)
        []
        >>> stl.getPointList(0.25, 0.25)
        [(<-0.0,0.25,0.25>, <...>), (<0.5,0.25,0.25>, <...>)]
        """
        xs = []
        points = {}
        for triangle in self.triangles:
            if triangle._bbox.contains_yz(y, z):
                I = triangle.intersect(y, z)
                if I is not None:
                    x = I[0].x
                    xs.append(x)
                    points[x] = I
        xs.sort()
        return [points[x] for x in xs]

    def make_layer(self, z, xsteps, ysteps, bbox, red):
        str = ''
        for y in bbox.getYiterator(ysteps):
            points = self.getPointList(y, z)

            def isMarked(x, points=points, n=len(points)):
                for j in range(0, n-1, 2):
                    if points[j][1].x < 0:
                        assert points[j+1][1].x > 0, points
                        if points[j][0].x <= x <= points[j+1][0].x:
                            return True
                    else:
                        # TODO figure out what to do
                        return False
                return False

            for x in bbox.getXiterator(xsteps):

                if isMarked(x):
                    if red:
                        str += '\xff\x00\x00'
                    else:
                        str += '\xff\xff\xff'
                else:
                    str += '\x00\x00\x00'

        return str


def generateRgb(z, stl, red, outf=None, width=1024, height=768):
    if outf is None:
        outf = sys.stdout
    if not isinstance(stl, Stl):
        stl = Stl(stl)
    bbox = stl._bbox.copy()
    sz = bbox.size()
    desired_aspect_ratio = 1. * height / width
    stl_aspect_ratio = 1. * sz.y / sz.x
    if desired_aspect_ratio > stl_aspect_ratio:
        sz.y = (desired_aspect_ratio / stl_aspect_ratio) * sz.x
    else:
        sz.x = (stl_aspect_ratio / desired_aspect_ratio) * sz.y
    bbox.set_size(sz)
    # TODO scale the STL
    outf.write(stl.make_layer(z, width, height, bbox, red))


def main():
    args = docopt.docopt(__doc__.replace('CMD', sys.argv[0]))

    if args['-T'] or args['--test']:
        import doctest
        verbose = args['-v'] or args['--verbose']
        failure_count, _ = doctest.testmod(verbose=verbose,
                                           optionflags=doctest.ELLIPSIS)
        sys.exit(failure_count)

    else:
        assert args['-f'] and args['-z']
        z = string.atof(args['-z'])
        filename = args['<filename>']
        stl = Stl(filename)
        if args['-r'] or args['--red']:
            red = True
        else:
            red = False
        profile = args['-p'] or args['--profile']
        if profile:
            import cProfile
            cProfile.run('generateRgb({0},"{1}",False)'.format(z, filename))
        else:
            # TODO enable red, width and height as command line args
            # generateRgb(z, filename, False)
            generateRgb(z, stl, red)


if __name__ == '__main__':
    main()
