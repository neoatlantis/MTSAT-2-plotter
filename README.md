Image plotter for MTSAT-2
=========================

This python program is able to plot the IR data retrived from MTSAT-2.

For more details on this piece of data, read
[this](ftp://mtsat-1r.cr.chiba-u.ac.jp/readme.txt). This is a detailed
explanation of data structure, the meaning, etc.

The plotter adds coastlines using data from [Nature Earth
Data](http://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-coastline/).

And the data is at the end shown using PIL(Python Image Library)'s `equalize`
method, to edit the contrast.

Known Issues
------------

0. The program is now not automatic. There is a requirement of looking up
   Tbb(Black Body Temperature) based on the table transmitted together with
   the data matrix, and the lookup table varies slightly. To be accurate,
   this lookup table should be automatically parsed.
