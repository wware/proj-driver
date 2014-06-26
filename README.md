Printer browser stuff
==

You need a browser window on the Mac that can be updated when necessary, and you position that browser window image under the resin tub. This runs off a little server on the Mac done with Flask or CherryPy or some such. The home page that the browser visits has Javascript which hits an endpoint asking for an MD5 of an image. If that MD5 is zero, the image element is hidden and all you see is the black background. Otherwise, if the MD5 is different from what the page was loaded with, it reloads the image. The little server reads the MD5 and the image from two files on the hard disk. The JS polling of the MD5 is very frequent, like every 100 msecs.

I'll need [templating](https://bitbucket.org/Lawouach/cherrypy-recipes/src/tip/web/templating/).