Stereolithographic printer
==

[Blog post](http://willware.blogspot.com/2014/07/homebrew-stereolithographic-3d-printer.html)

![A picture of the printer](http://2.bp.blogspot.com/-8E8wjE0TwTE/U7nzZKnxEEI/AAAAAAAAHo4/Qfy_TgaGZlY/s1600/IMG_20140705_205713.jpg "What it looks like")

Initially I tried shooting the projector up through the bottom of a glass pie plate, and followed examples of coating the inside of the pie
plate with Sylgard 184. But I couldn't get the Sylgard to work correctly; the cured resin kept sticking to it instead of sticking to my
build platform. So I took a page from the [Peachy Printer](https://www.youtube.com/watch?v=80HsW4HmUes) and projected downwards into a
bucket where a layer of resin floats on a larger quantity of salt water, because resin is expensive and salt water is very cheap.

My long-term intent, once I get several bugs and issues sorted out, is to publish plans, schematics, and software on
[Github](https://github.com) and [Instructables](http://instructables.com) or similar websites, and put the entire thing either in the
public domain or under some reasonably permissive [Creative Commons](http://creativecommons.org/) license like
[BY-SA](http://creativecommons.org/licenses/by-sa/3.0/).

Projector
--

InFocus IN114A, unmodified, 3000 lumens, 1024x768 resolution, HDMI input, 190 watts, 110 vac, $349 with $6 shipping

* http://www.newegg.com/Product/Product.aspx?Item=0B1-00PJ-00003
* http://www.infocus.com/projectors/product?pn=IN114A

Browser stuff
--

You need a browser window on the Mac that can be updated when necessary, and you position that browser window image under the resin tub. This runs off a little CherryPy server on the Mac. The home page that the browser visits has Javascript which hits an endpoint asking for an numerical index and a number of seconds. This polling happens fairly frequently (once or twice a second).
The file with that metadata is at `static/image.info` and is expos1ed with a URL of `/info`. The image is stored at `static/image.png` and
is exposed with a URL of `/image`. You don't want to use CherryPy's static mechanism to read these files, because they get cached and then
you don't get updated when they change.

If the JS hasn't seen that index before (which simply increments) then it un-hides an image element for that number of seconds.

The background of the web page is black so as to not cure any resin unnecessarily.

I might need [templating](https://bitbucket.org/Lawouach/cherrypy-recipes/src/tip/web/templating/).

On the Mac, use Cmd-Shift-F to make a browser tab take up the full screen.