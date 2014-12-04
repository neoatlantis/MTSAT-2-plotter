(到页底阅读中文版)

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
    * draw polygons, rectangles or lines onto the image, and calculate
      their representing geometric projection areas or length.

The data plotting program is also able to plot the VIS data retrieved from
MTSAT-2.

For more details on the data source, read
`ftp://mtsat-1r.cr.chiba-u.ac.jp/readme.txt`. This is a detailed explanation of
data structure, the meaning, etc.

The plotter adds vectorized lines using data from [Natural Earth
Data](http://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-coastline/).

------

获取，绘制和展示MTSAT-2卫星数据的系统
=====================================

本系统可以：

0. 从`ftp://mtsat-1r.cr.chiba-u.ac.jp`自动下载数据。
0. 将下载到的数据使用给定的色标（当前是美国海军实验室的IR-COLOR）绘图，保存成使用颜色索引的PNG图像。
0. 将上述图像针对地图服务拆分成块，对小放大比例的图形进行压缩，并将结果储存成可在网络服务器上公布的目录结构。
0. 利用一个网页在浏览器上提供对最近更新的图像的访问。这一浏览器基于`leaflet.js`开发，提供如下功能：
    * 展示不同时刻的图像结果;
    * 在不同通道(IR1-IR4)之间切换显示;
    * 动态添加或删除海岸线/国境线和经纬网;
    * 在图上用鼠标绘制多边形、矩形或多段线，计算它们对应的地理投影面积或长度。

绘图程序也能绘制MTSAT-2卫星的VIS通道上的数据。

要了解数据源的细节，请阅读`ftp://mtsat-1r.cr.chiba-u.ac.jp/readme.txt`。
这里有对源数据的结构和含义的详解等。

程序中绘制的矢量数据来自于[Natural Earth Data](http://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-coastline/).

(For English version scroll to top)
