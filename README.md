MTSAT-2 Satellite Dataset Retrieving, Plotting and Displaying
=============================================================

This is a system for:

0. retrieving datasets from `ftp://mtsat-1r.cr.chiba-u.ac.jp` regularly.
0. plotting retrieved data into images using configurable color
   scales(currently IR-COLOR used by NRL) and generate color palatted PNG
   files.
0. splitting the mentioned file into tiles, compressing them at small zoom
   levels, and arranging them into folders that can be served in a
   webserver and sent to web browser.
0. instructing the browser to display the recent updates with a single web
   page. There is a web viewer developed basing on `leaflet.js`, which
   provides an easy interface to:

    * display images at different time points;
    * switch between channels(IR1-IR4);
    * dynamically add/remove coastlines, graticules to/from the image;
    * draw polygons, rectangles or lines onto the image, and measure
      the representing geometric area or length.

The data plotting program is also able to plot the VIS data retrieved from
MTSAT-2.

For more details on the data source, read
[this](ftp://mtsat-1r.cr.chiba-u.ac.jp/readme.txt). This is a detailed
explanation of data structure, the meaning, etc.

The plotter adds coastlines using data from [Nature Earth
Data](http://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-coastline/).
