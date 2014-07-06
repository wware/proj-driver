#!/usr/bin/env python

from print3d import CherryPyServer, WHITE


class Octahedron(CherryPyServer):

    def supports(self):
        return [(0, 0)]

    def layer(self, z, img, duration=2000, color=WHITE):
        if z in range(0, 36):
            img.rectangle(-z, 0, 10, 7, color)
            img.rectangle(z, 0, 10, 7, color)
            img.rectangle(0, -z, 7, 10, color)
            img.rectangle(0, z, 7, 10, color)
        elif z in range(36, 40):
            img.rectangle(-z, 0, 10, 7, color)
            img.rectangle(z, 0, 10, 7, color)
            img.rectangle(0, -z, 7, 10, color)
            img.rectangle(0, z, 7, 10, color)
            img.hollow_diamond(0, 0, 40, 7, color)
        elif z in range(40, 43):
            img.rectangle(80 - z, 0, 10, 7, color)
            img.rectangle(z - 80, 0, 10, 7, color)
            img.rectangle(0, 80 - z, 7, 10, color)
            img.rectangle(0, z - 80, 7, 10, color)
            img.hollow_diamond(0, 0, 40, 7, color)
        elif z in range(43, 80):
            img.rectangle(80 - z, 0, 10, 7, color)
            img.rectangle(z - 80, 0, 10, 7, color)
            img.rectangle(0, 80 - z, 7, 10, color)
            img.rectangle(0, z - 80, 7, 10, color)
        else:
            self.stop()


if __name__ == '__main__':
    Octahedron.main()
