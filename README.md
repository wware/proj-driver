Printer browser stuff
==

You need a browser window on the Mac that can be updated when necessary, and you position that browser window image under the resin tub. This runs off a little CherryPy server on the Mac. The home page that the browser visits has Javascript which hits an endpoint asking for an index and a number of seconds. This polling happens fairly frequently (once or twice a second).

If the JS hasn't seen that index before (which simply increments) then it un-hides an image element for that number of seconds.

The background of the web page is black so as to not cure any resin unnecessarily.

I might need [templating](https://bitbucket.org/Lawouach/cherrypy-recipes/src/tip/web/templating/).

On the Mac, use Cmd-Shift-F to make a browser tab take up the full screen.

To use this stuff, set the thing up, and then type

```bash
echo "1 100" > static/image.info
# wait a few seconds, write a new picture to static/image.png, then
echo "2 100" > static/image.info
# and so on...
```